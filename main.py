import asyncio

from agent import Agent
from alarm import AlarmAgent
from artifact import CO2Sensor
from settings import sensor_coords, XMPP_SERVER, PASSWD


async def main():
	for sensor_id, coords in sensor_coords.items():
		sensor = CO2Sensor(f"co2sensor{sensor_id}@{XMPP_SERVER}", PASSWD)
		sensor.latitude = coords[1]
		sensor.longitude = coords[0]
		sensor.sensor_id = sensor_id
		sensor.start()


	agent = Agent(f"agent_co2@{XMPP_SERVER}", PASSWD)
	agent.start()

	alarm1 = AlarmAgent(f"alarm1@{XMPP_SERVER}", PASSWD)
	alarm1.zone_sensors = [1]
	alarm1.zone = 1
	alarm2 = AlarmAgent(f"alarm2@{XMPP_SERVER}", PASSWD)
	alarm2.zone_sensors = [2]
	alarm2.zone = 2
	alarm3 = AlarmAgent(f"alarm3@{XMPP_SERVER}", PASSWD)
	alarm3.zone_sensors = [4]
	alarm3.zone = 3
	alarm4 = AlarmAgent(f"alarm4@{XMPP_SERVER}", PASSWD)
	alarm4.zone_sensors = [3, 5]
	alarm4.zone = 4

	alarm1.start()
	alarm2.start()
	alarm3.start()
	alarm4.start()

	while True:
		try:
			await asyncio.sleep(1)
		except KeyboardInterrupt:
			break


if __name__ == '__main__':
	asyncio.run(main())
