import numpy as np

from app.util.units import convert_to_volts, to_volt_scale


def test_unit_scale():
    assert to_volt_scale("V") == 1.0
    assert to_volt_scale("mV") == 1e-3
    assert to_volt_scale("uV") == 1e-6
    assert to_volt_scale("nV") == 1e-9


def test_convert_to_volt():
    data = np.array([1.0, 2.0])
    out = convert_to_volts(data, "mV")
    assert np.allclose(out, np.array([1e-3, 2e-3]))
