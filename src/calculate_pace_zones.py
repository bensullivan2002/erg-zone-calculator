import json
from pathlib import Path


class PaceZoneCalculator:
    def __init__(self, two_km_time: float | int, precision: int) -> None:
        if not isinstance(two_km_time, (float, int)):
            raise TypeError("Invalid two_km_time format - must be a number")
        if not isinstance(precision, int):
            raise TypeError("Invalid precision format - must be an integer")
        if two_km_time <= 0:
            raise ValueError("Invalid two_km_time - must be greater than 0")
        if precision <= 0:
            raise ValueError("Invalid precision - must be greater than 0")
        self.two_km_time = two_km_time
        self.precision = precision

    def calculate_lower_bound_time_per_500m(
        self, zone: str, config_file_path: str
    ) -> float:
        if not isinstance(zone, str):
            raise TypeError("Invalid zone format - must be a string")
        if not isinstance(config_file_path, str):
            raise TypeError("Invalid config_file_path format - must be a string")
        try:
            with open(Path(config_file_path), "r") as f:
                config = json.load(f)
                lower_bound_coefficient = config[zone]["lower_bound"]
                lower_bound_time_per_500m = 500 / (
                    (2000 / self.two_km_time) * lower_bound_coefficient
                )
                return round(lower_bound_time_per_500m, self.precision)
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

    def calculate_upper_bound_time_per_500m(
        self, zone: str, config_file_path: str
    ) -> float:
        if not isinstance(zone, str):
            raise TypeError("Invalid zone format - must be a string")
        if not isinstance(config_file_path, str):
            raise TypeError("Invalid config_file_path format - must be a string")
        try:
            with open(Path(config_file_path), "r") as f:
                config = json.load(f)
                upper_bound_coefficient = config[zone]["upper_bound"]
                upper_bound_time_per_500m = 500 / (
                    (2000 / self.two_km_time) * upper_bound_coefficient
                )
                return round(upper_bound_time_per_500m, self.precision)
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
        pass
