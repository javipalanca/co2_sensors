import asyncio
import spade

from agent import Agent, CO2Sensor
from settings import sensor_coords


async def main():
	for sensor_id, coords in sensor_coords.items():
		sensor = CO2Sensor(f"co2sensor{sensor_id}@gtirouter.dsic.upv.es", "secret")
		sensor.latitude = coords[1]
		sensor.longitude = coords[0]
		sensor.sensor_id = sensor_id
		sensor.start()


	agent = Agent("agent_co2@gtirouter.dsic.upv.es", "secret")
	agent.start()

	while True:
		try:
			await asyncio.sleep(1)
		except KeyboardInterrupt:
			break


if __name__ == '__main__':
	asyncio.run(main())
