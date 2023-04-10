import spade


class Agent(spade.agent.Agent):

    async def setup(self):
        self.web.start(hostname="localhost", port=10000)
