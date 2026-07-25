import requests
import time
import csv
import os
from datetime import datetime

# --- System Configuration ---
API_URL = "http://192.168.0.120:25555/api/ets2/telemetry"
CSV_FILE = "job_transport_ground_truth.csv"
LOGGING_INTERVAL = 1.0  # Time between reads in seconds

# Columns for our CSV file, including Advanced Dynamics (Steering & G-Forces)
HEADERS = [
    "Timestamp", 
    "Source_City", "Destination_City", "Cargo", "Cargo_Mass_kg",
    "Speed_kmh", "Speed_Limit_kmh", "RPM", "Gear", "Throttle", "Brake", "Steering",
    "Accel_X", "Accel_Y", "Accel_Z",
    "Engine_Wear_%", "Tire_Wear_%", "Chassis_Wear_%",
    "Fuel_%", "Driving_Status"
]

def get_driving_status(speed, speed_limit, fuel_percent, brake_input, accel_x):
    """
    Evaluates real-time telemetry to assign a multi-state driving status.
    """
    statuses = []
    
    # 1. Speeding: Check if driving faster than the road limit
    if speed_limit > 0 and speed >= (speed_limit + 5):  # Allow 5 km/h tolerance
        statuses.append("Speeding")
        
    # 2. Hard Braking: Added speed condition to prevent logging while stationary
    if brake_input > 0.8 and speed > 15:
        statuses.append("Hard Braking")
        
    # 3. Harsh Cornering: Adjusted for realism.
    # Increased minimum speed to 30 km/h and G-Force threshold to 0.5 to ignore minor steering corrections.
    if speed > 30 and abs(accel_x) > 0.5:
        statuses.append("Harsh Cornering")
        
    # 4. Low Fuel: Warning threshold set below 15%
    if fuel_percent < 15:
        statuses.append("Low Fuel")
        
    return " | ".join(statuses) if statuses else "Normal"

def main():
    file_exists = os.path.isfile(CSV_FILE)
    
    print(" AI-Fleet-Simulator Logger Started...")
    print("-" * 60)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Initialize headers if the file is new
        if not file_exists:
            writer.writerow(HEADERS)
            print(" Created new file with advanced telemetry column names.")

        while True:
            start_time = time.time()  
            
            try:
                response = requests.get(API_URL, timeout=0.5)
                data = response.json()

                # --- NEW LOGIC: Pause Menu Detection ---
                # Extract game state to check if the user is in the pause menu
                game_state = data.get("game", {})
                is_paused = game_state.get("paused", False)

                if is_paused:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}]  Game Paused. Logging suspended...")
                    
                    # Calculate sleep time to maintain interval even while paused
                    elapsed_time = time.time() - start_time
                    time.sleep(max(0.0, LOGGING_INTERVAL - elapsed_time))
                    continue # Skip the rest of the loop (Do not write to CSV)
                # ---------------------------------------

                # 1. Job details
                job = data.get("job", {})
                source_city = job.get("sourceCity", "None")
                dest_city = job.get("destinationCity", "None")
                cargo = job.get("cargo", "None")
                cargo_mass = job.get("mass", 0)

                # 2. Basic Driving data
                truck = data.get("truck", {})
                speed_kmh = truck.get("speed", 0)
                rpm = truck.get("engineRpm", 0)
                gear = truck.get("displayedGear", 0)
                throttle = truck.get("userThrottle", 0.0)
                brake = truck.get("userBrake", 0.0)
                
                # 3. Advanced Dynamics (Steering and Acceleration/G-Forces)
                steering = truck.get("userSteer", 0.0)
                acceleration = truck.get("acceleration", {})
                accel_x = acceleration.get("x", 0.0)
                accel_y = acceleration.get("y", 0.0)
                accel_z = acceleration.get("z", 0.0)

                # 4. Navigation & Speed Limit
                nav = data.get("navigation", {})
                speed_limit = nav.get("speedLimit", 0)

                # 5. Truck health and fuel
                engine_wear = round(truck.get("wearEngine", 0) * 100, 2)
                tire_wear = round(truck.get("wearWheels", 0) * 100, 2)
                chassis_wear = round(truck.get("wearChassis", 0) * 100, 2)
                
                current_fuel = truck.get("fuel", 0)
                fuel_capacity = max(truck.get("fuelCapacity", 1), 1)
                fuel_percent = round((current_fuel / fuel_capacity) * 100, 1)

                # 6. Evaluate driving status using lateral G-Force (accel_x)
                driving_status = get_driving_status(speed_kmh, speed_limit, fuel_percent, brake, accel_x)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                # 7. Construct and append the row
                row = [
                    timestamp,
                    source_city, dest_city, cargo, cargo_mass,
                    round(speed_kmh, 1), speed_limit, round(rpm, 1), gear, round(throttle, 2), round(brake, 2), round(steering, 2),
                    round(accel_x, 3), round(accel_y, 3), round(accel_z, 3),
                    engine_wear, tire_wear, chassis_wear,
                    fuel_percent, driving_status
                ]
                
                writer.writerow(row)
                file.flush()

                print(f"[{timestamp}] Speed: {int(speed_kmh)} km/h | Accel_X: {round(accel_x, 2)} | Status: {driving_status}")

            except requests.exceptions.RequestException:
                print(" Could not connect to the Telemetry Server")
            except KeyError as e:
                print(f" Missing data from the game: {e}")
            except Exception as e:
                print(f" Unexpected Error: {e}")

            # Dynamic sleep calculation
            elapsed_time = time.time() - start_time
            sleep_time = max(0.0, LOGGING_INTERVAL - elapsed_time)
            time.sleep(sleep_time)

if __name__ == "__main__":
    main()
