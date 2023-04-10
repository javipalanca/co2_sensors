import spade

from agent import Agent


async def main():
    agent = Agent("agent_co2@gtirouter.dsic.upv.es", "secret")
    await agent.start()

    await spade.wait_until_finished(agent)

if __name__ == '__main__':
    spade.run(main())

