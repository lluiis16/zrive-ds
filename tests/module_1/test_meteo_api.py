""" This is a dummy example to show how to import code from src/ for testing"""

from src.module_1.module_1_meteo_api import get_data_meteo_api, CITIES

def test_get_data_for_madrid():
    df = get_data_meteo_api("Madrid", **CITIES["Madrid"])
    assert not df.empty
    assert "temperature_2m_mean" in df.columns
    assert "time" in df.columns    