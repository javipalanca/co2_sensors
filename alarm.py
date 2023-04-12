import json

import spade
from spade.message import Message
from spade_artifact import ArtifactMixin

from settings import XMPP_SERVER


def send_msg(msg, agent):
    class SendMsg(spade.behaviour.OneShotBehaviour):
        def __init__(self, msg):
            super().__init__()
            self.msg = msg

        async def run(self):
            await self.send(self.msg)

    agent.add_behaviour(SendMsg(msg))


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
        msg = Message(to=f"agent_co2@{XMPP_SERVER}", body=json.dumps({"zone": self.zone, "value": prom, "alarm": alarm}))
        msg.set_metadata("performative", "alarm")
        send_msg(msg, self)
