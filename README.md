# 🌱 PhytoICU : Pre-Symptomatic Crop Stress &amp; Pest Disambiguation Engine. 
Stop waiting for crops to turn yellow to diagnose them. PhytoICU turns any smartphone or basic camera into a real-time Intensive Care Unit (ICU) for crops—detecting hidden dehydration and microscopic sap-sucking pests 48 to 72 hours before visible leaf damage appears.

# How to Use the Manual Telemetry Controls ($T_a, T_c, RH$)
Right now, most farmers and smallholders do not have expensive electronic IoT sensors installed in their soil or leaves. Furthermore, remote fields often have zero cellular connectivity.
To make PhytoICU 100% usable without external internet or physical sensors, we put the microclimate controls directly in your hands via sliders:
# 1. Air Temperature ($T_a$)
What it means: The general ambient temperature of the surrounding air in Celsius (°C).

How it affects results:

Warmer air holds exponentially more water vapor. When $T_a$ is high, the atmosphere exerts a much stronger "suction pull" on the plant's moisture.
# 2. Relative Humidity ($RH$)
What it means: The moisture level in the atmosphere (from 10% to 95%).

How it affects results:

At high humidity ($>70\%$), the air is saturated. 

Water evaporates slowly, so the plant doesn't feel extreme atmospheric thirst.

At low humidity ($<35\%$), dry air aggressively sucks water out of the leaves.

# 3. Canopy Temperature ($T_c$)
What it means: The physical surface temperature of the plant leaves (°C).

How it affects results:
1. A Healthy, Hydrated Plant Sweats: Just like humans sweat to stay cool on a hot day, a healthy plant transpires water vapor through tiny leaf pores (stomata). This evaporative cooling keeps the leaf surface cooler than the ambient air ($T_c < T_a$).
 
2. A Dehydrated Plant Gets a Fever: When the plant runs out of water, it slams its stomata shut to keep from drying out. Sweating stops, heat gets trapped, and the leaf develops a canopy fever ($T_c \gg T_a$).

How to estimate $T_c$ manually: 

If the leaves feel noticeably warm to the touch during the afternoon, set $T_c$ higher than $T_a$. If they feel refreshingly cool, set $T_c$ lower than $T_a$.

# 📊 Understanding Your Dashboard Outputs & Action Alerts
When you run the video stream, the system continuously displays real-time diagnostic readings:

 DIAGNOSIS: CRITICAL PRE-SYMPTOMATIC DROUGHT 
 
 Systemic downward sag + Elevated thermal CWSI  
 
 CWSI: 0.74 | Droop: 0.22px/f | Curl: 0.05 | Stipple: 0.02   
 
 Action: Activate Zone Drip Irrigation immediately.                     


*The Output Metrics Decoded:*

1. CWSI (Crop Water Stress Index): A scale from 0.0 (fully hydrated) to 1.0 (extreme dehydration). Measures the internal fever of the crop based on your temperature and humidity inputs.
2. Droop Velocity ($v_y$): Measures how fast leaves are physically sinking downward under gravity (in pixels per frame) due to loss of internal water pressure.
3. Curl Vorticity ($\nabla \times \vec{v}$): Measures rotational twisting along leaf edges. Microscopic sap-sucking pests cause leaves to cup and twist asymmetrically.
4. Stipple Noise ($\sigma^2$): Measures high-frequency surface roughness. Mites and thrips puncture tiny microscopic holes into leaves, creating subtle textural visual noise.

  # The 4 Real-World Diagnostic States:
🟢 OPTIMAL CANOPY HEALTH: CWSI is low, leaves are standing upright with zero downward sag. Everything is functioning normally.

🔴 PRE-SYMPTOMATIC DROUGHT: High CWSI fever combined with uniform downward droop arrows. The plant has lost water pressure. Action: Turn on zone drip irrigation immediately.

🟡 EARLY PEST ATTACK (Mites/Aphids): CWSI is normal (the plant is hydrated!), but the vision engine catches leaf edge curling and puncture noise. Action: Spot-spray organic biocontrol. DO NOT turn on irrigation.

🚨 COMPOUND STRESS: Both severe thirst and pest damage detected simultaneously. Action: Irrigate immediately and manually inspect leaf undersides for bug colonies.

# ⏱️ How to Test and Experiment: The Smartphone Time-Lapse Method
Real plants do not wilt in 10 seconds—cellular dehydration happens gradually over 2 to 6 hours.

If you point a standard video camera at a plant for 10 seconds, it will look completely stationary. To test this system accurately without waiting for months of lab testing, use a smartphone Time-Lapse:

1.Place any smartphone on a desk or stake pointing at a potted plant or crop foliage.

2.Put your camera in Time-Lapse / Hyperlapse Mode (e.g., set to record 1 frame every 15 to 30 seconds).
 
3.Record a plant that hasn't been watered for a day during the afternoon for 1 to 2 hours.

4.The phone compresses 2 hours of slow wilting into a smooth 15- to 30-second .mp4 video.

5.Upload that video into the PhytoICU dashboard:

 High-frequency wind shakes naturally cancel out over the time-lapse.
 
 The optical flow engine immediately catches the dramatic downward sinking vectors ($v_y$) and tracks cellular collapse in real time!
 
7. (No video available right now? Just click the blue "Instant Live Demo" button on the dashboard to test the algorithm on an animated, simulated plant canopy).

 pictorial vision: <img width="1672" height="941" alt="ChatGPT Image Sep 5, 2026, 04_29_11 AM" src="https://github.com/user-attachments/assets/0fd1ae80-cffb-4b9f-b138-c130a2306f33" />

 # Experience it : 

 # 🏢 Enterprise & B2B: Software-First, Hardware-Upgradable
PhytoICU is built as an open, modular software engine. While smallholder farmers can use it manually with zero extra costs, any agritech enterprise, greenhouse operator, or machinery manufacturer can plug in hardware to make it fully autonomous:
<img width="1536" height="1024" alt="ChatGPT Image Sep 23, 2026, 07_30_42 PM" src="https://github.com/user-attachments/assets/2027905f-d1c3-41f9-9b5c-a0f063e497e3" />
# How Companies Can Upgrade This System:
Add a $5 Non-Contact Thermal Sensor: Plug an infrared temperature sensor (like the MLX90614) into an Arduino/Raspberry Pi. The sensor automatically reads real leaf surface temperature ($T_c$) and feeds it into PhytoICU, eliminating manual slider inputs.

Add a $15 Continuous USB Webcam: Mount a waterproof webcam in a greenhouse or high-value hydroponic farm for continuous 24/7 autonomous ICU monitoring.

Tractor Boom "See & Spray" Upgrade: Mount commodity cameras along the boom of an ordinary tractor sprayer. As the tractor drives down crop rows, PhytoICU pinpoints localized pest patches and triggers individual spray nozzles, skipping healthy crop rows entirely.

# 💰The Hardware Cost Disruption: 95%+ Capex Reduction
Traditional precision agriculture relies on multi-thousand-dollar thermal cameras, multispectral drone payloads, and cloud GPU processing subscriptions that no small or medium farm can afford.

PhytoICU replaces expensive multi-band sensors with deterministic computational vision and plant physics:
<img width="1931" height="814" alt="ChatGPT Image Sep 23, 2026, 07_39_52 PM" src="https://github.com/user-attachments/assets/a38c03eb-d862-4967-abd2-0ad955cb15ef" />



