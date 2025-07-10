import json
from calculate_pace_zones import PaceZoneCalculator

def main():
    calculator = PaceZoneCalculator(415, 1)
    config_file_path = "config/pace_zones.json"
    with open(config_file_path, "r") as f:
        zones = json.load(f)
    for key in zones:
        try:
            lower_bound = calculator.calculate_lower_bound_time_per_500m(key, config_file_path)
            upper_bound = calculator.calculate_upper_bound_time_per_500m(key, config_file_path)
            print(f"Zone: {key}, Lower Bound: {lower_bound}, Upper Bound: {upper_bound}")
        except Exception as e:
            print(f"Error calculating for zone {key}: {e}")

if __name__ == "__main__":
    main()
