import unittest
import asyncio
from discord.ext.prometheus import PrometheusCog
from discord.ext import commands
from discord import Intents

class TestCog(unittest.TestCase):
	"""
	Testing the PrometheusCog class
	"""

	def test_can_be_instanciated(self):
		event_loop = asyncio.new_event_loop()
		asyncio.set_event_loop(event_loop)

		async def run_test():
			bot = commands.Bot(
				command_prefix='!',
				intents=Intents.all()
			)

			PrometheusCog(bot)

		coro = asyncio.coroutine(run_test)
		event_loop.run_until_complete(coro())
		event_loop.close()
