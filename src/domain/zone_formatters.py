from abc import ABC, abstractmethod
from datetime import timedelta


class ZoneFormatter(ABC):
    """Abstract base class for zone value formatters."""

    @abstractmethod
    def format_value(self, value: int | float | None) -> str:
        """Format a numeric zone value for display.

        Args:
            value: The numeric zone value to format, or None for open-ended zones

        Returns:
            Formatted string representation
        """
        pass

    def format_zone_bounds(self, lower: int | float | None, upper: int | float | None) -> str:
        """Format zone bounds as a range.

        Args:
            lower: Lower bound value or None for open-ended
            upper: Upper bound value or None for open-ended

        Returns:
            Formatted range string (e.g., "108-144bpm", ">180bpm", "<100bpm")
        """
        if lower is None and upper is None:
            return "No bounds"
        elif lower is None:
            return f"<{self.format_value(upper)}"
        elif upper is None:
            return f">{self.format_value(lower)}"
        else:
            return f"{self.format_value(lower)}-{self.format_value(upper)}"


class HRFormatter(ZoneFormatter):
    """Formatter for heart rate values."""

    def format_value(self, value: int | float | None) -> str:
        """Format heart rate value.

        Args:
            value: Heart rate as integer or None for open-ended

        Returns:
            Formatted heart rate (e.g., "108bpm") or empty string for None
        """
        if value is None:
            return ""
        return f"{int(value)}bpm"


class PaceFormatter(ZoneFormatter):
    """Formatter for pace values (time per 500m)."""

    def format_value(self, value: int | float | None) -> str:
        """Format pace value as time.

        Args:
            value: Time in seconds or None for open-ended

        Returns:
            Formatted time (e.g., "1:45/500m") or empty string for None
        """
        if value is None:
            return ""
        td = timedelta(seconds=value)
        minutes = int(td.total_seconds() // 60)
        seconds = int(td.total_seconds() % 60)
        return f"{minutes}:{seconds:02d}/500m"


class VerbosePaceFormatter(ZoneFormatter):
    """Verbose formatter for pace values."""

    def format_value(self, value: int | float | None) -> str:
        """Format pace value as verbose time.

        Args:
            value: Time in seconds or None for open-ended

        Returns:
            Formatted time (e.g., "1 min 45 sec/500m") or empty string for None
        """
        if value is None:
            return ""
        td = timedelta(seconds=value)
        minutes = int(td.total_seconds() // 60)
        seconds = int(td.total_seconds() % 60)

        if minutes == 0:
            return f"{seconds} sec/500m"
        elif seconds == 0:
            return f"{minutes} min/500m"
        else:
            return f"{minutes} min {seconds} sec/500m"