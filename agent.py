import asyncio
import random

import spade
from spade_artifact import Artifact, ArtifactMixin


class Agent(ArtifactMixin, spade.agent.Agent):

	async def setup(self):
		self.web.start(hostname="localhost", port=10000)
		self.sensors = {}
		for i in range(20):
			self.sensors[i] = None
			await self.artifacts.focus(f"co2sensor{i}", self.artifact_callback)
			print(f"Subscribed to co2sensor{i}")

	async def artifact_callback(self, artifact, payload):
		lat, lon, sensor_id, perception = payload.split(",")
		self.sensors[int(sensor_id)] = [float(lat), float(lon), float(perception)]
		print(f"Sensor {sensor_id} perception: {perception}")


class CO2Sensor(Artifact):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.latitude = 0
		self.longitude = 0
		self.sensor_id = 0

	async def run(self) -> None:
		while True:
			perception = random.random()
			await self.publish(f"{self.latitude},{self.longitude},{self.sensor_id},{perception}")
			print(f"Sensor {self.sensor_id} perception: {perception}")
			await asyncio.sleep(1)
