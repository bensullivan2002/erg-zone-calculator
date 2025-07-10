import json
from pathlib import Path


class PaceZoneCalculator:
    def __init__(self, two_km_time: str, precision: int) -> None:
        if not isinstance(two_km_time, (str)):
            raise TypeError("Invalid two_km_time format - must be a string")
        if not isinstance(precision, int):
            raise TypeError("Invalid precision format - must be an integer")
        parsed_two_km_time = _parse_time_str_to_seconds(two_km_time)
        if parsed_two_km_time <= 0:
            raise ValueError("Invalid two_km_time - must be greater than 0")
        if precision <= 0:
            raise ValueError("Invalid precision - must be greater than 0")
        self.two_km_time = parsed_two_km_time
        self.precision = precision

    def calculate_lower_bound_time_per_500m(
        self, zone: str, config_file_path: str
    ) -> float | str:
        if not isinstance(zone, str):
            raise TypeError("Invalid zone format - must be a string")
        if not isinstance(config_file_path, str):
            raise TypeError("Invalid config_file_path format - must be a string")
        try:
            with open(Path(config_file_path), "r") as f:
                config = json.load(f)
                lower_bound_coefficient = config[zone]["lower_bound"]
                if lower_bound_coefficient is None:
                    return f"No lower pace bound for zone {zone}"
                lower_bound_time_per_500m = 500 / (
                    (2000 / self.two_km_time) * lower_bound_coefficient
                )
                return _format_seconds_to_time_str(round(lower_bound_time_per_500m, self.precision), self.precision)
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
    ) -> float | str:
        if not isinstance(zone, str):
            raise TypeError("Invalid zone format - must be a string")
        if not isinstance(config_file_path, str):
            raise TypeError("Invalid config_file_path format - must be a string")
        try:
            with open(Path(config_file_path), "r") as f:
                config = json.load(f)
                upper_bound_coefficient = config[zone]["upper_bound"]
                if upper_bound_coefficient is None:
                    return f"No upper pace bound for zone {zone}"
                upper_bound_time_per_500m = 500 / (
                    (2000 / self.two_km_time) * upper_bound_coefficient
                )
                return _format_seconds_to_time_str(round(upper_bound_time_per_500m, self.precision), self.precision)
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

def _parse_time_str_to_seconds(time_str: str) -> float:
    minutes, seconds = time_str.split(":")
    return int(minutes) * 60 + float(seconds)

def _format_seconds_to_time_str(seconds: float, precision: int) -> str:
    minutes = int(seconds // 60)
    sec = seconds % 60
    sec_format = f"04.{precision}f"
    return f"{minutes:02d}:{format(sec, sec_format)}"
