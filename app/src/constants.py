"""
Business domain constants for validation and rules.
"""


# Heart Rate validation bounds
class HeartRateValidation:
    MIN_HEART_RATE = 100
    MAX_HEART_RATE = 240


# Pace validation bounds
class PaceValidation:
    MIN_DISTANCE_METERS = 500
    MAX_DISTANCE_METERS = 10000
    MIN_TIME_SECONDS = 60
    MAX_TIME_SECONDS = 3600
