"""Unit handling and conversion for thermodynamic calculations."""

import pint

# Create global unit registry
ureg = pint.UnitRegistry()

# Define base units
K = ureg.kelvin
Pa = ureg.pascal
bar = ureg.bar
atm = ureg.atm
mol = ureg.mol
kg = ureg.kg
J = ureg.joule
m3 = ureg.meter**3

# Define useful combinations
J_per_mol = J / mol
Pa_m3_per_mol2 = Pa * m3 / mol**2
m3_per_mol = m3 / mol


def convert_temperature(value: float, from_unit: str, to_unit: str = "K") -> float:
    """Convert temperature between units.

    Parameters
    ----------
    value : float
        Temperature value
    from_unit : str
        Source unit (e.g., 'K', 'C', 'F')
    to_unit : str
        Target unit, default 'K'

    Returns
    -------
    float
        Converted temperature in target unit
    """
    quantity = ureg.Quantity(value, from_unit)
    return quantity.to(to_unit).magnitude


def convert_pressure(value: float, from_unit: str, to_unit: str = "Pa") -> float:
    """Convert pressure between units.

    Parameters
    ----------
    value : float
        Pressure value
    from_unit : str
        Source unit (e.g., 'Pa', 'bar', 'atm', 'psi')
    to_unit : str
        Target unit, default 'Pa'

    Returns
    -------
    float
        Converted pressure in target unit
    """
    quantity = ureg.Quantity(value, from_unit)
    return quantity.to(to_unit).magnitude
