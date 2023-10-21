import unittest
from discord.ext.prometheus import PrometheusCog
from discord.ext import commands
from discord import Intents

class TestCog(unittest.IsolatedAsyncioTestCase):
	"""
	Testing the PrometheusCog class
	"""

	async def test_can_be_instantiated(self):
		bot = commands.Bot(
			command_prefix='!',
			intents=Intents.all()
		)
		cog = PrometheusCog(bot)
		await bot.add_cog(cog)
		cog.collect()
		await bot.close()
