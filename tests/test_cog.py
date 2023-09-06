import unittest
from discord.ext.prometheus import PrometheusCog
from discord.ext import commands
from discord import Intents

class TestCog(unittest.TestCase):
	"""
	Testing the PrometheusCog class
	"""

	async def test_can_be_instanciated(self):

		bot = commands.Bot(
			command_prefix='!',
			intents=Intents.all()
		)

		print('test')

		PrometheusCog(bot)
