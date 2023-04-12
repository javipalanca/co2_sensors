import asyncio

from agent import Agent
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

	while True:
		try:
			await asyncio.sleep(1)
		except KeyboardInterrupt:
			break


if __name__ == '__main__':
	asyncio.run(main())
