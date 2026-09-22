import os
import time
import math
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
import uvicorn

app = FastAPI(title="PhytoICU - High Accuracy Engine")
os.makedirs("uploads", exist_ok=True)

# =====================================================================
# 1. HIGH-ACCURACY VISION ENGINE
# =====================================================================
class CanopyVisionEngine:
    def __init__(self):
        self.prev_gray = None
        # EMA (Exponential Moving Average) State Variables for Smooth Accuracy
        self.ema_vy = 0.0
        self.ema_curl = 0.0
        self.ema_stip = 0.0
        self.alpha = 0.15  # Smoothing factor (Lower = smoother but slower reaction)

    def isolate_canopy(self, frame):
        """High-Accuracy Masking: HSV + Morphological Noise Cleaning."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_green = np.array([25, 40, 40], dtype=np.uint8)
        upper_green = np.array([85, 255, 255], dtype=np.uint8)
        raw_mask = cv2.inRange(hsv, lower_green, upper_green)

        # Morphological Opening (Removes tiny noise specs like soil glare)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        clean_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, kernel)
        return clean_mask

    def compute_stippling_entropy(self, gray_frame, mask):
        lap = cv2.Laplacian(gray_frame, cv2.CV_64F)
        leaf_pixels = lap[mask > 0]
        if len(leaf_pixels) == 0:
            return 0.0
        var = float(np.var(leaf_pixels))
        return min(1.0, max(0.0, (var - 120.0) / 450.0))

    def analyze_frame(self, frame):
        h, w = frame.shape[:2]
        if w > 640:
            frame = cv2.resize(frame, (640, int(h * (640 / w))))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.isolate_canopy(frame)
        annotated = frame.copy()

        raw_vy = 0.0
        raw_curl = 0.0
        raw_stip = self.compute_stippling_entropy(gray, mask)

        if self.prev_gray is not None and self.prev_gray.shape == gray.shape:
            # Optical Flow
            flow = cv2.calcOpticalFlowFarneback(
                self.prev_gray, gray, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )
            vx = flow[..., 0]
            vy = flow[..., 1]

            plant_mask = mask > 0
            plant_vy = vy[plant_mask]

            # Deadband Filter: Ignore micro-vibrations < 0.08px
            if len(plant_vy) > 0:
                downward = plant_vy[plant_vy > 0.08]
                if len(downward) > 0:
                    raw_vy = float(np.mean(downward))

            dvy_dx = cv2.Sobel(vy, cv2.CV_64F, 1, 0, ksize=3)
            dvx_dy = cv2.Sobel(vx, cv2.CV_64F, 0, 1, ksize=3)
            curl = np.abs(dvy_dx - dvx_dy)
            plant_curl = curl[plant_mask]

            if len(plant_curl) > 0:
                raw_curl = float(np.mean(plant_curl))

            # Visual Overlays
            step = 25
            for y in range(0, frame.shape[0], step):
                for x in range(0, frame.shape[1], step):
                    if mask[y, x] > 0:
                        dx, dy = flow[y, x]
                        if abs(curl[y, x]) > 0.8:
                            cv2.circle(annotated, (x, y), 3, (0, 255, 255), -1)
                        elif dy > 0.15:
                            # BUG FIX: Added tipLength=0.3 to prevent OpenCV crash
                            cv2.arrowedLine(annotated, (x, y), (int(x + dx * 3), int(y + dy * 3)), (0, 0, 255), 1, tipLength=0.3)

        self.prev_gray = gray

        # Apply Exponential Moving Average (EMA) to stabilize outputs
        self.ema_vy = (self.alpha * raw_vy) + ((1 - self.alpha) * self.ema_vy)
        self.ema_curl = (self.alpha * raw_curl) + ((1 - self.alpha) * self.ema_curl)
        self.ema_stip = (self.alpha * raw_stip) + ((1 - self.alpha) * self.ema_stip)

        return annotated, self.ema_vy, self.ema_curl, self.ema_stip

# =====================================================================
# 2. PHYSICS & SciML ENGINE
# =====================================================================
class CanopyPhysicsEngine:
    def __init__(self):
        self.a = 2.5
        self.b = -1.8

    def calculate_vpd(self, air_temp: float, rel_humidity: float) -> float:
        e_sat = 0.61078 * math.exp((17.27 * air_temp) / (air_temp + 237.3))
        e_act = e_sat * (rel_humidity / 100.0)
        return max(0.1, e_sat - e_act)

    def compute_cwsi(self, canopy_temp: float, air_temp: float, rel_humidity: float) -> float:
        dT = canopy_temp - air_temp
        vpd = self.calculate_vpd(air_temp, rel_humidity)
        dT_lower = self.a + self.b * vpd
        dT_upper = self.a + 4.5
        cwsi = (dT - dT_lower) / (dT_upper - dT_lower)
        return max(0.0, min(1.0, float(cwsi)))

    def disambiguate_stress(self, vy: float, curl: float, stippling: float, cwsi: float) -> dict:
        norm_droop = min(1.0, vy / 1.0)
        norm_curl = min(1.0, curl / 0.7)

        drought_score = (0.6 * cwsi) + (0.4 * norm_droop)
        pest_score = (0.5 * norm_curl) + (0.5 * stippling)

        if pest_score >= 0.48 and drought_score < 0.45:
            status = "EARLY PEST ATTACK DETECTED"
            subtext = "High margin vorticity & stippling (Aphids/Mites)"
            color = (0, 255, 255)
            protocol = "Apply biocontrol. DO NOT over-irrigate."
        elif drought_score >= 0.55 and pest_score < 0.40:
            status = "PRE-SYMPTOMATIC DROUGHT"
            subtext = "Systemic downward sag + Elevated thermal CWSI"
            color = (0, 0, 255)
            protocol = "Activate Zone Drip Irrigation immediately."
        elif drought_score >= 0.50 and pest_score >= 0.50:
            status = "COMPOUND STRESS (Pest + Drought)"
            subtext = "Cellular puncture combined with root water deficit"
            color = (0, 0, 255)
            protocol = "Irrigate zone & inspect leaf undersides."
        else:
            status = "HEALTHY CANOPY"
            subtext = "Optimal transpiration baseline maintained"
            color = (0, 255, 0)
            protocol = "No intervention required."

        return {
            "drought_score": round(drought_score, 2), "pest_score": round(pest_score, 2),
            "cwsi": round(cwsi, 2), "vy": round(vy, 3), "curl": round(curl, 3), "stippling": round(stippling, 3),
            "status": status, "subtext": subtext, "color": color, "protocol": protocol
        }

# =====================================================================
# 3. SYNTHETIC EMULATOR
# =====================================================================
def generate_synthetic_leaf_frame(t: float, tc: float):
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (24, 28, 36)
    
    stress_factor = max(0.0, min(1.0, (tc - 26.0) / 12.0))
    sag = int(40 * stress_factor + 10 * math.sin(t * 0.5))
    twist = int(15 * math.cos(t * 0.7)) if stress_factor > 0.4 else 0

    cv2.ellipse(img, (320, 220 + sag), (140, 65 + twist), 25, 0, 360, (35, 175, 55), -1)
    cv2.ellipse(img, (290, 240 + sag), (120, 50 - twist), -20, 0, 360, (28, 145, 45), -1)
    
    if stress_factor > 0.5:
        noise = np.random.randint(0, 100, (60, 60), dtype=np.uint8)
        img[200:260, 300:360, 0] = np.maximum(img[200:260, 300:360, 0], noise)
        img[200:260, 300:360, 1] = np.maximum(img[200:260, 300:360, 1], noise)

    return img

# =====================================================================
# 4. STREAM GENERATOR
# =====================================================================
def stream_pipeline(video_path: str, air_temp: float, canopy_temp: float, humidity: float):
    vision = CanopyVisionEngine()
    physics = CanopyPhysicsEngine()
    
    use_synthetic = not os.path.exists(video_path) or video_path.endswith("synthetic")
    cap = None if use_synthetic else cv2.VideoCapture(video_path)
    t = 0.0

    while True:
        if use_synthetic:
            frame = generate_synthetic_leaf_frame(t, canopy_temp)
            t += 0.12
            time.sleep(0.035)
        else:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break
            time.sleep(0.01)

        annotated, vy, curl, stip = vision.analyze_frame(frame)
        cwsi = physics.compute_cwsi(canopy_temp, air_temp, humidity)
        res = physics.disambiguate_stress(vy, curl, stip, cwsi)

        cv2.rectangle(annotated, (10, 10), (630, 105), (15, 23, 42), -1)
        cv2.rectangle(annotated, (10, 10), (630, 105), res["color"], 2)

        cv2.putText(annotated, f"DIAGNOSIS: {res['status']}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, res["color"], 2)
        cv2.putText(annotated, res["subtext"], (20, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (203, 213, 225), 1)
        cv2.putText(annotated, f"CWSI: {res['cwsi']} | Droop: {res['vy']}px/f | Curl: {res['curl']} | Stipple: {res['stippling']}",
                    (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(annotated, f"Action: {res['protocol']}", (20, 98), cv2.FONT_HERSHEY_SIMPLEX, 0.42, res["color"], 1)

        success, buffer = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not success:
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

# =====================================================================
# 5. FASTAPI ROUTES & DASHBOARD
# =====================================================================
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>PhytoICU - High Accuracy Engine</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #0b0f17; color: #f8fafc; margin: 0; padding: 25px; }
            .container { max-width: 950px; margin: auto; background: #161b22; padding: 25px; border-radius: 12px; border: 1px solid #30363d; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            .panel { background: #21262d; padding: 20px; border-radius: 8px; border: 1px solid #30363d; }
            label { display: block; margin-top: 12px; font-weight: 600; font-size: 14px; color: #cbd5e1; }
            input[type="range"] { width: 100%; margin-top: 6px; accent-color: #2ea043; }
            #feed { width: 100%; border-radius: 8px; background: #000; min-height: 400px; border: 2px solid #30363d; display: block; margin-top: 20px; }
            button { background: #2ea043; color: white; border: none; padding: 12px 18px; font-size: 15px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 15px; }
            button:hover { background: #238636; }
            .btn-blue { background: #1f6feb; }
            .btn-blue:hover { background: #388bfd; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>🌱 PhytoICU: High-Accuracy Diagnostic Stream</h2>
            <p style="color: #8b949e; font-size: 14px; margin-top: -5px;">Active Filtering: EMA Smoothing + Morphological Masking + Kinematic Deadbands</p>

            <div class="grid">
                <div class="panel">
                    <h3 style="margin-top:0;">1. Telemetry Console</h3>
                    <label>Air Temp ($T_a$): <span id="ta_disp">28.0</span> °C</label>
                    <input type="range" id="ta" min="15" max="45" step="0.5" value="28.0" oninput="ta_disp.innerText=this.value; updateStream();">

                    <label>Canopy Temp ($T_c$): <span id="tc_disp">33.5</span> °C</label>
                    <input type="range" id="tc" min="15" max="45" step="0.5" value="33.5" oninput="tc_disp.innerText=this.value; updateStream();">

                    <label>Relative Humidity: <span id="rh_disp">45</span>%</label>
                    <input type="range" id="rh" min="10" max="95" step="1" value="45" oninput="rh_disp.innerText=this.value; updateStream();">
                </div>

                <div class="panel">
                    <h3 style="margin-top:0;">2. Input Source</h3>
                    <input type="file" id="video_file" accept="video/*" style="margin-top: 10px;">
                    <button onclick="launchStream(false)">▶ Run On Uploaded Video</button>
                    <button onclick="launchStream(true)" class="btn-blue">⚡ Instant Live Demo (Synthetic)</button>
                </div>
            </div>

            <div style="margin-top: 25px;">
                <img id="feed" alt="Video stream will display here upon execution...">
            </div>
        </div>

        <script>
            let activeMode = 'synthetic';
            let uploadedFile = '';

            function updateStream() {
                const ta = document.getElementById('ta').value;
                const tc = document.getElementById('tc').value;
                const rh = document.getElementById('rh').value;
                const feed = document.getElementById('feed');
                
                let fileParam = activeMode === 'synthetic' ? 'synthetic' : encodeURIComponent(uploadedFile);
                
                // Cache-Buster appended to force browser to instantly reload the stream
                feed.src = `/api/stream?filename=${fileParam}&ta=${ta}&tc=${tc}&rh=${rh}&t=${new Date().getTime()}`;
            }

            async function launchStream(useSynthetic) {
                activeMode = useSynthetic ? 'synthetic' : 'upload';

                if (!useSynthetic) {
                    const fileInput = document.getElementById('video_file');
                    if (!fileInput.files[0]) {
                        alert("Please select a video file first, or click 'Instant Live Demo'!");
                        return;
                    }
                    const formData = new FormData();
                    formData.append('video', fileInput.files[0]);

                    const uploadRes = await fetch('/api/upload', { method: 'POST', body: formData });
                    const data = await uploadRes.json();
                    uploadedFile = data.filename;
                }
                updateStream();
            }

            // Launch synthetic automatically
            window.onload = () => { launchStream(true); };
        </script>
    </body>
    </html>
    """

@app.post("/api/upload")
async def upload_file(video: UploadFile = File(...)):
    dest = os.path.join("uploads", video.filename)
    with open(dest, "wb") as f:
        f.write(await video.read())
    return JSONResponse({"filename": video.filename})

@app.get("/api/stream")
async def get_video_stream(filename: str = Query("synthetic"), ta: float = Query(28.0), tc: float = Query(33.5), rh: float = Query(45.0)):
    video_path = os.path.join("uploads", filename)
    return StreamingResponse(
        stream_pipeline(video_path, air_temp=ta, canopy_temp=tc, humidity=rh),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)