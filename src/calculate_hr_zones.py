import json
from pathlib import Path


class HRZoneCalculator:
    def __init__(self, max_HR: int) -> None:
        if not isinstance(max_HR, (int)):
            raise TypeError("Invalid max_HR format - must be an integer")
        if max_HR <= 0:
            raise ValueError("Invalid max_HR - must be greater than 0")
        self.max_HR = max_HR

    def calculate_lower_bound_HR(self, zone: str, config_file_path: str) -> str:
        if not isinstance(zone, str):
            raise TypeError("Invalid zone format - must be a string")
        if not isinstance(config_file_path, str):
            raise TypeError("Invalid config_file_path format - must be a string")
        try:
            with open(Path(config_file_path), "r") as f:
                config = json.load(f)
                lower_bound_coefficient = config[zone]["lower_bound"]
                if lower_bound_coefficient is None:
                    return f"No lower HR bound for zone {zone}"
                lower_bound_HR = self.max_HR * lower_bound_coefficient
                return f"{int(lower_bound_HR)}bpm"
        except FileNotFoundError as e:
            print(f"Config file not found at {config_file_path}")
            raise e
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format in config file at {config_file_path}")
            raise e
        except KeyError as e:
            print(f"Invalid zone {zone} in config file at {config_file_path}")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e

    def calculate_upper_bound_HR(self, zone: str, config_file_path: str) -> str:
        if not isinstance(zone, str):
            raise TypeError("Invalid zone format - must be a string")
        if not isinstance(config_file_path, str):
            raise TypeError("Invalid config_file_path format - must be a string")
        try:
            with open(Path(config_file_path), "r") as f:
                config = json.load(f)
                upper_bound_coefficient = config[zone]["upper_bound"]
                if upper_bound_coefficient is None:
                    return f"No upper HR bound for zone {zone}"
                upper_bound_HR = self.max_HR * upper_bound_coefficient
                return f"{int(upper_bound_HR)}bpm"
        except FileNotFoundError as e:
            print(f"Config file not found at {config_file_path}")
            raise e
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format in config file at {config_file_path}")
            raise e
        except KeyError as e:
            print(f"Invalid zone {zone} in config file at {config_file_path}")
            raise e
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise e
