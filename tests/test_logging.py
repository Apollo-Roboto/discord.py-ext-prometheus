import unittest

from discord.ext.prometheus import PrometheusLoggingHandler

class TestLoggingHandler(unittest.TestCase):
	"""
	Testing the PrometheusLoggingHandler class
	"""

	def test_can_be_instanciated(self):
		PrometheusLoggingHandler()
