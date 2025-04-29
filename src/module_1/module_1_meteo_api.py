""" This is a dummy example """

import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

API_URL = "https://archive-api.open-meteo.com/v1/archive?"

COORDINATES = {
 "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
 "London": {"latitude": 51.507351, "longitude": -0.127758},
 "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}
VARIABLES = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]

START_DATE = "2010-01-01"
END_DATE = "2020-12-31"

def call_api(url: str, params: dict, retries: int = 3):
    for _ in range(retries):
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                print(" Respuesta recibida")
                return response.json()
            elif response.status_code == 429:
                print("Rate limit alcanzado. Esperando...")
                time.sleep(60)
            else:
                print(f"Error {response.status_code}: {response.text}")
                time.sleep(3)
        except Exception as e:
            print("Error:", e)
    raise Exception("No se pudo conectar con la API")
    


def get_data_meteo_api(city: str, latitude: float, longitude: float) -> pd.DataFrame:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": VARIABLES,
        "timezone": "auto"
    }
    data = call_api(API_URL, params)

    if "daily" not in data or "time" not in data["daily"]:
        raise ValueError("Respuesta inesperada de la API")

    df = pd.DataFrame(data["daily"])
    df["city"] = city
    df["time"] = pd.to_datetime(df["time"])
    return df

def resample_data(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    return df.set_index("time").groupby("city").resample(freq).mean().reset_index()

def plot_variable(df: pd.DataFrame, variable: str, save_path: str):
    plt.figure(figsize=(12, 6))
    for city in df["city"].unique():
        subset = df[df["city"] == city]
        plt.plot(subset["time"], subset[variable], label=city)
    plt.title(f"Evolución de {variable}")
    plt.xlabel("Tiempo")
    plt.ylabel(variable)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f" Gráfico guardado: {save_path}")    

def main():
    from pathlib import Path
    print(" Ejecutando main()")

    all_dfs = []
    for city, coords in COORDINATES.items():
        print(f"Descargando datos de {city}...")
        df = get_data_meteo_api(city, coords["latitude"], coords["longitude"])
        all_dfs.append(df)

    df_total = pd.concat(all_dfs)
    df_monthly = resample_data(df_total)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    for var in VARIABLES:
        plot_variable(df_monthly, var, save_path=output_dir / f"{var}.png")
        print(f"Gráfico guardado: {output_dir / f'{var}.png'}")


if __name__ == "__main__":
    main()