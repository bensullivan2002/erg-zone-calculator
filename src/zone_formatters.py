from abc import ABC, abstractmethod
from datetime import timedelta


class ZoneFormatter(ABC):
    """Abstract base class for zone value formatters."""

    @abstractmethod
    def format_value(self, value: int | float) -> str:
        """Format a numeric zone value for display.

        Args:
            value: The numeric zone value to format

        Returns:
            Formatted string representation
        """
        pass

    def format_zone_bounds(self, lower: int | float, upper: int | float) -> str:
        """Format zone bounds as a range.

        Args:
            lower: Lower bound value
            upper: Upper bound value

        Returns:
            Formatted range string (e.g., "108-144bpm")
        """
        return f"{self.format_value(lower)}-{self.format_value(upper)}"


class HRFormatter(ZoneFormatter):
    """Formatter for heart rate values."""

    def format_value(self, value: int | float) -> str:
        """Format heart rate value.

        Args:
            value: Heart rate as integer

        Returns:
            Formatted heart rate (e.g., "108bpm")
        """
        return f"{int(value)}bpm"


class PaceFormatter(ZoneFormatter):
    """Formatter for pace values (time per 500m)."""

    def format_value(self, value: int | float) -> str:
        """Format pace value as time.

        Args:
            value: Time in seconds

        Returns:
            Formatted time (e.g., "1:45/500m")
        """
        td = timedelta(seconds=value)
        minutes = int(td.total_seconds() // 60)
        seconds = int(td.total_seconds() % 60)
        return f"{minutes}:{seconds:02d}/500m"


class VerbosePaceFormatter(ZoneFormatter):
    """Verbose formatter for pace values."""

    def format_value(self, value: int | float) -> str:
        """Format pace value as verbose time.

        Args:
            value: Time in seconds

        Returns:
            Formatted time (e.g., "1 min 45 sec/500m")
        """
        td = timedelta(seconds=value)
        minutes = int(td.total_seconds() // 60)
        seconds = int(td.total_seconds() % 60)

        if minutes == 0:
            return f"{seconds} sec/500m"
        elif seconds == 0:
            return f"{minutes} min/500m"
        else:
            return f"{minutes} min {seconds} sec/500m"
