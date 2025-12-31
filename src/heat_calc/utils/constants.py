"""Physical constants and reference correlation metadata.

Constants used in heat transfer calculations with SI units (K, J, Pa, etc.).
"""

# Thermodynamic Constants
BOLTZMANN_CONSTANT: float = 1.380649e-23  # J/K (exact as of SI 2019)
GAS_CONSTANT_UNIVERSAL: float = 8.31446261815324  # J/(mol·K) (exact as of SI 2019)
AVOGADRO_NUMBER: float = 6.02214076e23  # particles/mol (exact as of SI 2019)
STEFAN_BOLTZMANN: float = 5.670374419e-8  # W/(m²·K⁴)

# Physical Properties
STANDARD_GRAVITY: float = 9.80665  # m/s²
ATMOSPHERIC_PRESSURE: float = 101325  # Pa
ABSOLUTE_ZERO: float = 0.0  # K
TRIPLE_POINT_WATER: float = 273.16  # K

# Common Reference Temperatures
ROOM_TEMPERATURE: float = 293.15  # K (20°C)
STANDARD_TEMPERATURE: float = 298.15  # K (25°C)
NORMAL_BOILING_POINT_WATER: float = 373.15  # K (100°C)

# Conversion Factors
HEAT_CONVERSION_BTU_TO_J: float = 1055.06  # J/BTU
HEAT_CONVERSION_CAL_TO_J: float = 4.184  # J/cal

# Correlation Sources and Metadata
LMTD_CORRELATIONS = {
    "counterflow": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "formula": "LMTD = (ΔT1 - ΔT2) / ln(ΔT1 / ΔT2)",
        "reference_chapter": 10,
        "applicable_range": "All temperature differences",
        "correction_factor_required": False,
    },
    "parallel_flow": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "formula": "LMTD = (ΔT1 - ΔT2) / ln(ΔT1 / ΔT2)",
        "reference_chapter": 10,
        "applicable_range": "All temperature differences",
        "correction_factor_required": False,
    },
    "crossflow_unmixed_both": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "formula": "LMTD_corrected = F * LMTD_counterflow",
        "reference_chapter": 10,
        "reference_figure": 10.15,
        "correction_factor_required": True,
        "correction_based_on": ["P", "R"],  # effectiveness and capacity ratio
    },
    "crossflow_mixed_one_unmixed": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "formula": "LMTD_corrected = F * LMTD_counterflow",
        "reference_chapter": 10,
        "reference_figure": 10.16,
        "correction_factor_required": True,
        "correction_based_on": ["P", "R"],
    },
}

NTU_CORRELATIONS = {
    "counterflow": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 11,
        "formula": "effectiveness = (1 - exp(-(1-R)*NTU)) / (1 - R*exp(-(1-R)*NTU))",
        "min_ntu": 0.0,
        "max_ntu": float("inf"),
        "parameter_r_range": (0.0, 1.0),
    },
    "parallel_flow": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 11,
        "formula": "effectiveness = (1 - exp(-NTU*(1+R))) / (1 + R)",
        "min_ntu": 0.0,
        "max_ntu": float("inf"),
        "parameter_r_range": (0.0, 1.0),
    },
    "crossflow_unmixed": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 11,
        "reference_table": 11.3,
        "formula": "effectiveness = 1 - exp((-NTU**0.22/R) * (exp(-R*NTU**0.78) - 1))",
        "min_ntu": 0.0,
        "max_ntu": 3.0,
        "parameter_r_range": (0.0, 1.0),
        "note": "Approximate; exact values from correlation charts",
    },
}

CONVECTION_CORRELATIONS = {
    "laminar_flat_plate": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 7,
        "correlation_type": "Nusselt-Reynolds-Prandtl",
        "formula": "Nu = 0.664 * Re^0.5 * Pr^(1/3)",
        "valid_reynolds_range": (0.1, 5e5),
        "valid_prandtl_range": (0.6, 2000),
        "conditions": "laminar boundary layer, constant heat flux",
    },
    "turbulent_flat_plate": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 7,
        "correlation_type": "Nusselt-Reynolds-Prandtl",
        "formula": "Nu = 0.037 * Re^0.8 * Pr^(1/3)",
        "valid_reynolds_range": (5e5, 1e7),
        "valid_prandtl_range": (0.6, 60),
        "conditions": "turbulent boundary layer, smooth surface",
    },
    "dittus_boelert_pipe": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 8,
        "correlation_type": "Nusselt-Reynolds-Prandtl",
        "formula": "Nu = 0.023 * Re^0.8 * Pr^n",
        "note": "n = 0.4 for heating, n = 0.3 for cooling",
        "valid_reynolds_range": (10000, 1e6),
        "valid_prandtl_range": (0.7, 100),
        "conditions": "fully developed turbulent flow in circular pipe",
    },
    "cylinder_crossflow": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 7,
        "reference_table": 7.2,
        "correlation_type": "Nusselt-Reynolds-Prandtl",
        "valid_reynolds_range": (0.1, 1e6),
        "note": "Use table-based correlation; constants depend on Re",
    },
    "natural_convection_vertical_plate": {
        "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
        "reference_chapter": 9,
        "correlation_type": "Nusselt-Rayleigh",
        "formula": "Nu = 0.54 * Ra^(1/4)",
        "valid_rayleigh_range": (1e4, 1e9),
        "conditions": "laminar natural convection on vertical surface",
    },
}

INSULATION_OPTIMIZATION = {
    "source": "Incropera et al. - Fundamentals of Heat and Mass Transfer",
    "reference_chapter": 3,
    "economic_optimization": {
        "formula": "Q_loss = k*A*(T_surface - T_ambient) / (L_insulation + k*h_conv)",
        "objective": "Minimize annual cost = (material cost) + (heat loss cost)",
        "constraint": "Surface temperature must be <= max allowed (safety/comfort)",
    },
}

# Temperature-dependent property correlation metadata
PROPERTY_CORRELATIONS = {
    "dynamic_viscosity": {
        "units": "Pa·s",
        "source": "NIST webbook or property tables",
        "temperature_range": (200, 2000),  # K
        "note": "Strongly temperature dependent",
    },
    "thermal_conductivity": {
        "units": "W/(m·K)",
        "source": "NIST webbook or property tables",
        "temperature_range": (200, 2000),
        "note": "Moderate temperature dependence",
    },
    "specific_heat": {
        "units": "J/(kg·K)",
        "source": "NIST webbook or property tables",
        "temperature_range": (200, 2000),
        "note": "Weak temperature dependence for liquids, moderate for gases",
    },
}

# Validation tolerance defaults
VALIDATION_TOLERANCES = {
    "incropera_example": 0.02,  # 2% tolerance for textbook examples
    "nist_reference": 0.05,  # 5% tolerance for NIST data
    "typical_calculation": 0.10,  # 10% tolerance for general calculations
}

# Performance guidelines
PERFORMANCE_TARGET_MS = 100  # ms - all calculations should complete within this
PERFORMANCE_EXPECTED_MS = 10  # ms - expected typical execution time
