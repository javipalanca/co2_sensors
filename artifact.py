import asyncio
import json
import math

import pandas as pd
from dateutil.parser import parse
from spade_artifact import Artifact


class CO2Sensor(Artifact):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.latitude = 0
        self.longitude = 0
        self.sensor_id = 0

    def load_dataset(self):
        df = pd.read_csv("Balizas_peligro_CO2.csv")
        df = df[["FECHA", "ID_BALIZA", "MEDIA"]]
        df = df[df["ID_BALIZA"] == self.sensor_id]
        # df to list
        self.time_serie = df.values.tolist()

    def load_dataset_salamanca(self):
        with open(f"NODOS_CO2/{self.sensor_id}.json") as f:
            data = json.load(f)
            self.time_serie = [[row["Fecha"], self.sensor_id, row["CO2"]*1.5] for row in data]
        # sort list of lists by date
        self.time_serie.sort(key=lambda x: parse(x[0]))

    def get_perception(self):
        perception = self.time_serie.pop(0)
        date = parse(perception[0])
        data = perception[2] if not math.isnan(perception[2]) else 0
        return date, data

    async def run(self) -> None:
        self.load_dataset_salamanca()
        while True:
            date, perception = self.get_perception()
            await self.publish(f"{date},{self.sensor_id},{perception}")
            print(f"Sensor {self.sensor_id} date: {date} perception: {perception}")
            await asyncio.sleep(1)
