import json
from collections import defaultdict

import spade
from dateutil.parser import parse
from spade_artifact import ArtifactMixin

from predict import Predictor
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
		self.web.add_get("/leaflet_awesome_number_markers.css", self.static_controller,
						 template="templates/leaflet_awesome_number_markers.css")
		self.web.add_get("/leaflet_awesome_number_markers.js", self.static_controller,
						 template="templates/leaflet_awesome_number_markers.js")
		self.web.app.router.add_static("/images/", path="templates/images/")
		self.alarms = {1: {"value": 0, "alarm": "success"},
					   2: {"value": 0, "alarm": "success"},
					   3: {"value": 0, "alarm": "success"},
					   4: {"value": 0, "alarm": "success"}}
		self.zones = {1: [1, 2], 2: [3], 3: [4], 4: [5]}
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
			idx = min(7, len(self.sensors[sensor_id]) - 1)
			if self.sensors[sensor_id]:
				for perception in self.sensors[sensor_id][:-idx]:
					data.append([lat, lon, perception[1] / MAX_CO2])
		return data

	async def ts_json_controller(self, request):
		data = defaultdict(list)
		zones = {}
		for z in self.zones:
			zones[z] = defaultdict(list)
		for sensor_id, coords in self.sensor_coords.items():
			zone = [k for k, v in self.zones.items() if sensor_id in v][0]
			if self.sensors[sensor_id]:
				for date, co2 in self.sensors[sensor_id]:  # [:-idx]:
					if co2 != 0:
						data[date].append(co2)
						zones[zone][date].append(co2)

		labels = list(data.keys())
		labels.sort()
		means = []
		meanzones = defaultdict(list)
		zones_pred = {}
		for date in labels:
			means.append(sum(data[date]) / len(data[date]))
			for z in zones.keys():
				try:
					meanzones[z].append(sum(zones[z][date]) / len(zones[z][date]))
				except ZeroDivisionError:
					if len(meanzones[z]) > 1:
						meanzones[z].append(meanzones[z][-1])
					else:
						meanzones[z].append(None)

		for z in zones.keys():
			pred = Predictor(labels, meanzones[z])
			fut_dates, fut_pred = pred.predict(7)
			zones_pred[z] = [None] * (len(meanzones[z]) - 1) + meanzones[z][-1:] + fut_pred[-7:]

		labels = [str(label) for label in labels]

		# predictions
		mean_predictor = Predictor(labels, means)
		fut_dates, fut_means = mean_predictor.predict(7)

		fut_dates = fut_dates[-7:]
		fut_means = [None] * (len(means) - 1) + means[-1:] + fut_means[-7:]

		return {"labels": labels, "means": means, "zones": meanzones,
				"fut_dates": fut_dates, "fut_means": fut_means,
				"zones_pred": zones_pred
				}

	async def index_controller(self, request):
		return {"alarms": self.alarms}

	async def static_controller(self, request):
		return {}
