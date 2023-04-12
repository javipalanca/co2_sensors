import json
from collections import defaultdict

import spade
from dateutil.parser import parse
from spade_artifact import ArtifactMixin

from settings import sensor_coords, XMPP_SERVER, MAX_CO2


class Agent(ArtifactMixin, spade.agent.Agent):

	async def setup(self):
		self.web.start(hostname="localhost", port=10000)
		self.web.add_get("/data.json", self.map_json_controller, template=None)
		self.web.add_get("/ts.json", self.ts_json_controller, template=None)
		self.web.add_get("/", self.index_controller, template="templates/index.html")
		self.web.add_get("/leaflet-idw.js", self.static_controller, template="templates/leaflet-idw.js")
		self.web.add_get("/main.js", self.static_controller, template="templates/main.js")
		self.web.add_get("/chart-helper.js", self.static_controller, template="templates/chart-helper.js")
		self.alarms = {1: {"value": 0, "alarm": "green"}, 2: {"value": 0, "alarm": "green"}, 3: {"value": 0, "alarm": "green"}}
		self.sensors = defaultdict(list)
		self.sensor_coords = sensor_coords
		self.add_behaviour(self.AlarmBehaviour())
		for sensor_id in sensor_coords.keys():
			await self.artifacts.focus(f"co2sensor{sensor_id}@{XMPP_SERVER}", self.artifact_callback)
			# print(f"Subscribed to co2sensor{i}")

	def artifact_callback(self, artifact, payload):
		date, sensor_id, perception = payload.split(",")
		date = parse(date).date()
		self.sensors[int(sensor_id)].append((date, float(perception)))
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
			idx = min(7, len(self.sensors[sensor_id])-1)
			if self.sensors[sensor_id]:
				for perception in self.sensors[sensor_id][:-idx]:
					data.append([lat, lon, perception[1]/MAX_CO2])
		return data

	async def ts_json_controller(self, request):
		data = defaultdict(list)
		for sensor_id, coords in self.sensor_coords.items():
			idx = min(7, len(self.sensors[sensor_id])-1)
			if self.sensors[sensor_id]:
				for perception in self.sensors[sensor_id][:-idx]:
					data[perception[0]].append(perception[1])

		labels = list(data.keys())
		labels.sort()
		means = []
		for label in labels:
			means.append(sum(data[label])/len(data[label]))
		labels = [str(label) for label in labels]
		return {"labels": labels, "means": means}

	async def index_controller(self, request):
		return {"alarms": self.alarms}

	async def static_controller(self, request):
		return {}


