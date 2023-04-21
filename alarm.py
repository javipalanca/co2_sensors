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
            await self.artifacts.focus(f"co2sensor{i}@{XMPP_SERVER}", self.artifact_callback)
            print(f"AlarmAgent subscribed to co2sensor{i}")

    def artifact_callback(self, artifact, payload):
        date, sensor_id, perception = payload.split(",")
        perception = float(perception)
        self.sensors[int(sensor_id)] = perception
        print(f"AlarmAgent: Sensor {sensor_id} perception: {perception}")
        if perception:
            if perception > 1300:
                alarm = "danger"
            elif perception >= 700:
                alarm = "warning"
            else:
                alarm = "success"
            msg = Message(to=f"agent_co2@{XMPP_SERVER}", body=json.dumps({"zone": self.zone, "value": perception, "alarm": alarm}))
            msg.set_metadata("performative", "alarm")
            send_msg(msg, self)
