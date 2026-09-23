import math
import numpy as np

class CanopyPhysicsEngine:
    def __init__(self, baseline_intercept: float = 2.4, baseline_slope: float = -1.75):
        self.a = baseline_intercept
        self.b = baseline_slope

    def calculate_vpd(self, air_temp: float, rel_humidity: float) -> float:
        e_sat = 0.61078 * math.exp((17.27 * air_temp) / (air_temp + 237.3))
        e_act = e_sat * (rel_humidity / 100.0)
        return max(0.1, e_sat - e_act)

    def compute_cwsi(self, canopy_temp: float, air_temp: float, rel_humidity: float) -> float:
        dT = canopy_temp - air_temp
        vpd = self.calculate_vpd(air_temp, rel_humidity)
        dT_lower = self.a + (self.b * vpd)
        dT_upper = self.a + 4.5
        cwsi = (dT - dT_lower) / (dT_upper - dT_lower)
        return float(np.clip(cwsi, 0.0, 1.0))

    def evaluate_dual_diagnostics(self, vy: float, curl: float, stippling: float, cwsi: float) -> dict:
        norm_droop = float(np.clip(vy / 1.1, 0.0, 1.0))
        norm_curl = float(np.clip(curl / 0.75, 0.0, 1.0))

        drought_score = (0.60 * cwsi) + (0.40 * norm_droop)
        pest_score = (0.50 * norm_curl) + (0.50 * stippling)

        if pest_score >= 0.52 and drought_score < 0.48:
            diagnosis = "EARLY PEST ATTACK (Aphids / Spider Mites)"
            prescription = "Deploy Targeted Biocontrol / Spot-spray; Do NOT irrigate (prevents root-rot)."
            alert_code = "PEST"
        elif drought_score >= 0.58 and pest_score < 0.42:
            diagnosis = "PRE-SYMPTOMATIC DROUGHT STRESS"
            prescription = "Activate Zone Drip Irrigation immediately (Stomata beginning closure)."
            alert_code = "DROUGHT"
        elif drought_score >= 0.50 and pest_score >= 0.48:
            diagnosis = "COMPOUND STRESS (Water Deficit + Pest Colonization)"
            prescription = "Moderate drip irrigation & inspect leaf abaxial surfaces with 10x loupe."
            alert_code = "COMPOUND"
        else:
            diagnosis = "OPTIMAL CANOPY HEALTH"
            prescription = "Transpiration and structural cell turgor are within baseline."
            alert_code = "HEALTHY"

        return {
            "drought_score": round(drought_score, 3),
            "pest_score": round(pest_score, 3),
            "cwsi": round(cwsi, 3),
            "droop_velocity": round(vy, 3),
            "curl_vorticity": round(curl, 3),
            "stippling_index": round(stippling, 3),
            "diagnosis": diagnosis,
            "prescription": prescription,
            "alert_code": alert_code
        }