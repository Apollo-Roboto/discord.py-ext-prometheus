import unittest

from discord.ext.prometheus import PrometheusCog
from discord.ext import commands
from discord import Intents

class TestCog(unittest.TestCase):
	"""
	Testing the PrometheusCog class
	"""

	def test_can_be_instanciated(self):
		bot = commands.Bot(
			command_prefix='!',
			intents=Intents.all()
		)

		PrometheusCog(bot)
