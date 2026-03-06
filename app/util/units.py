UNIT_TO_VOLT = {
    "V": 1.0,
    "mV": 1e-3,
    "uV": 1e-6,
    "nV": 1e-9,
}


def to_volt_scale(unit: str) -> float:
    if unit not in UNIT_TO_VOLT:
        raise ValueError(f"Unsupported unit: {unit}")
    return UNIT_TO_VOLT[unit]


def convert_to_volts(values, unit: str):
    scale = to_volt_scale(unit)
    return values * scale
