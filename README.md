# AI Fleet Simulator: IoT Telematics & Driver Behavior Analytics

## What This Does
- Extracts real vehicle telemetry from ETS2
- Trains ML model to detect driving behavior
- Achieves 99.22% accuracy on unseen data
- Identifies: harsh cornering, speeding, normal driving

## The Data
- 66,000 seconds (18+ hours) of continuous driving
- 10,000+ km simulated
- Speed, RPM, throttle, brake, steering, G-forces

## Results
- Normal driving: 99% detected
- Harsh cornering: 97% detected
- Speeding: 96% detected

## Why This Matters
Instead of testing with real cars (expensive, slow),
use this simulator to validate telematics platforms.
Cost savings: 80-90%. Speed: 10x faster.

## How to Run
[instructions]

## Technologies
Python, scikit-learn, ETS2 API, Random Forest, Data Engineering
