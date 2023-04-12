import asyncio
import json
import math
from collections import defaultdict

import pandas as pd

import spade
from dateutil.parser import parse
from spade.message import Message
from spade_artifact import Artifact, ArtifactMixin

from settings import sensor_coords


def send_msg(msg, agent):
	class SendMsg(spade.behaviour.OneShotBehaviour):
		def __init__(self, msg):
			super().__init__()
			self.msg = msg

		async def run(self):
			await self.send(self.msg)

	agent.add_behaviour(SendMsg(msg))


class Agent(ArtifactMixin, spade.agent.Agent):

	async def setup(self):
		self.web.start(hostname="localhost", port=10000)
		self.web.add_get("/data.json", self.map_json_controller, template=None)
		self.web.add_get("/", self.index_controller, template="templates/index.html")
		self.web.add_get("/leaflet-idw.js", self.static_controller, template="templates/leaflet-idw.js")
		self.web.add_get("/main.js", self.static_controller, template="templates/main.js")
		self.alarms = {1: {"value": 0, "alarm": "green"}, 2: {"value": 0, "alarm": "green"}, 3: {"value": 0, "alarm": "green"}}
		self.sensors = defaultdict(list)
		self.sensor_coords = sensor_coords
		self.add_behaviour(self.AlarmBehaviour())
		for sensor_id in sensor_coords.keys():
			await self.artifacts.focus(f"co2sensor{sensor_id}@gtirouter.dsic.upv.es", self.artifact_callback)

	# print(f"Subscribed to co2sensor{i}")

	def artifact_callback(self, artifact, payload):
		date, sensor_id, perception = payload.split(",")
		self.sensors[int(sensor_id)].append(float(perception))
		print(f"Received data: Sensor {sensor_id} perception: {perception}")

	class AlarmBehaviour(spade.behaviour.CyclicBehaviour):
		async def run(self):
			msg = await self.receive(timeout=10)
			if msg:
				print(f"Received alarm message: {msg.body}")
				data = json.loads(msg.body)
				self.agent.alarms[data["zone"]] = {"value": data["value"], "alarm": data["alarm"]}

	async def map_json_controller(self, request):
		data = []
		for sensor_id, coords in self.sensor_coords.items():
			lat, lon = coords
			if self.sensors[sensor_id]:
				for perception in self.sensors[sensor_id]:
					data.append([lat, lon, perception/30000])
		return data

	async def index_controller(self, request):
		return {"alarms": self.alarms}

	async def static_controller(self, request):
		return {}


class AlarmAgent(ArtifactMixin, spade.agent.Agent):
	async def setup(self):
		self.sensors = {}
		for i in self.zone_sensors:
			await self.artifacts.focus(f"co2sensor{i}", self.artifact_callback)
			print(f"AlarmAgent subscribed to co2sensor{i}")

	async def artifact_callback(self, artifact, payload):
		lat, lon, sensor_id, perception = payload.split(",")
		self.sensors[int(sensor_id)] = float(perception)
		print(f"Sensor {sensor_id} perception: {perception}")
		prom = sum(self.sensors.values()) / len(self.sensors)
		if prom > 30000:
			alarm = "red"
		elif prom >= 5000:
			alarm = "orange"
		elif prom >= 701:
			alarm = "yellow"
		else:
			alarm = "green"
		msg = Message(to="agent_co2@gtirouter.dsic.upv.es", body=json.dumps({"zone": self.zone, "value": prom, "alarm": alarm}))
		msg.set_metadata("performative", "alarm")
		send_msg(msg, self)


class CO2Sensor(Artifact):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.latitude = 0
		self.longitude = 0
		self.sensor_id = 0

	def load_dataset(self):
		df = pd.read_csv("Balizas_peligro_CO2.csv")
		self.df = df[["FECHA", "ID_BALIZA", "MEDIA"]]
		self.df = self.df[self.df["ID_BALIZA"] == self.sensor_id]
		# df to list
		self.df = self.df.values.tolist()

	def get_perception(self):
		perception = self.df.pop(0)
		date = parse(perception[0])
		data = perception[2] if not math.isnan(perception[2]) else 0
		return date, data

	async def run(self) -> None:
		self.load_dataset()
		while True:
			date, perception = self.get_perception()
			await self.publish(f"{date},{self.sensor_id},{perception}")
			print(f"Sensor {self.sensor_id} date: {date} perception: {perception}")
			await asyncio.sleep(10)
