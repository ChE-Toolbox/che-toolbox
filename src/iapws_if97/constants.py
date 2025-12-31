"""IAPWS-IF97 thermodynamic constants and region boundaries.

Defines critical points, triple points, region boundaries, and numerical
parameters for IAPWS-IF97 calculations.
"""

from typing import Final

# Critical Point (IAPWS-IF97)
CRITICAL_PRESSURE_PA: Final[float] = 22.064e6  # Pa (22.064 MPa)
CRITICAL_TEMPERATURE_K: Final[float] = 373.946  # K
CRITICAL_DENSITY_KG_M3: Final[float] = 322.0  # kg/m³

# Triple Point (water)
TRIPLE_POINT_PRESSURE_PA: Final[float] = 611.657  # Pa
TRIPLE_POINT_TEMPERATURE_K: Final[float] = 273.16  # K (0.01°C)

# Region 1 Boundaries (Compressed Liquid Water)
# Region 1: High pressure, low to medium temperature
REGION1_PRESSURE_MIN_PA: Final[float] = 16.53e6  # Reference pressure in IAPWS-IF97
REGION1_PRESSURE_MAX_PA: Final[float] = 863.91e6  # 863.91 MPa (upper limit)
REGION1_TEMPERATURE_MIN_K: Final[float] = 273.15  # K (triple point)
REGION1_TEMPERATURE_MAX_K: Final[float] = 863.15  # K

# Region 2 Boundaries (Superheated Steam)
# Region 2: Low to medium pressure, medium to high temperature
REGION2_PRESSURE_MAX_PA: Final[float] = 100e6  # 100 MPa
REGION2_TEMPERATURE_MIN_K: Final[float] = 273.15  # K
REGION2_TEMPERATURE_MAX_K: Final[float] = 863.15  # K

# Region 3 Boundaries (Supercritical Fluid)
# Region 3: High pressure and temperature, near critical point
REGION3_PRESSURE_MIN_PA: Final[float] = 16.6e6  # 16.6 MPa
REGION3_PRESSURE_MAX_PA: Final[float] = 863.91e6  # Upper limit
REGION3_TEMPERATURE_MIN_K: Final[float] = 623.15  # K
REGION3_TEMPERATURE_MAX_K: Final[float] = 863.15  # K

# Saturation Line Boundaries
SATURATION_PRESSURE_MIN_PA: Final[float] = 611.657  # Pa (triple point)
SATURATION_PRESSURE_MAX_PA: Final[float] = 22.064e6  # Pa (critical point)
SATURATION_TEMPERATURE_MIN_K: Final[float] = 273.16  # K (triple point)
SATURATION_TEMPERATURE_MAX_K: Final[float] = 647.096  # K (critical point)

# Global Valid Range
GLOBAL_PRESSURE_MIN_PA: Final[float] = 611.657  # Pa
GLOBAL_PRESSURE_MAX_PA: Final[float] = 863.91e6  # Pa
GLOBAL_TEMPERATURE_MIN_K: Final[float] = 273.15  # K
GLOBAL_TEMPERATURE_MAX_K: Final[float] = 863.15  # K

# Numerical Parameters
SINGULARITY_THRESHOLD: Final[float] = 0.05  # 5% normalized distance from critical point
CONVERGENCE_TOLERANCE_T_K: Final[float] = 1e-6  # 1 µK absolute tolerance
CONVERGENCE_TOLERANCE_P_PA: Final[float] = 1e-3  # 1 mPa absolute tolerance
MAX_ITERATIONS: Final[int] = 100  # Maximum iterations for root-finding

# Unit Conversions
KELVIN_TO_CELSIUS_OFFSET: Final[float] = 273.15
PA_TO_MPA: Final[float] = 1e-6
PA_TO_BAR: Final[float] = 1e-5
PA_TO_ATM: Final[float] = 9.86923e-6
