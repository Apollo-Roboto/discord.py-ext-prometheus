import logging
from prometheus_client import start_http_server, Counter, Gauge
from discord.ext import commands
from discord import Interaction, InteractionType

log = logging.getLogger('prometheus')

METRIC_PREFIX = 'discord_'

CONNECTION_GAUGE = Gauge(
	METRIC_PREFIX + 'connected',
	'Determines if the bot is connected to Discord',
)
ON_INTERACTION_COUNTER = Counter(
	METRIC_PREFIX + 'event_on_interaction',
	'Amount of interactions',
	['command'],
)
ON_COMMAND_COUNTER = Counter(
	METRIC_PREFIX + 'event_on_command',
	'Amount of commands',
	['command'],
)
GUILD_GAUGE = Gauge(
	METRIC_PREFIX + 'stat_total_guilds',
	'Amount of guild this bot is a member of'
)
CHANNEL_GAUGE = Gauge(
	METRIC_PREFIX + 'stat_total_channels',
	'Amount of channels this bot is has access to'
)
USER_GAUGE = Gauge(
	METRIC_PREFIX + 'stat_total_users',
	'Amount of users this bot can see'
)
COMMANDS_GAUGE = Gauge(
	METRIC_PREFIX + 'stat_total_commands',
	'Amount of commands'
)

class PrometheusCog(commands.Cog):
	"""
	A Cog to be added to a discord bot. The prometheus server will start once the bot is ready
	using the `on_ready` listener.
	"""

	def __init__(self, bot: commands.Bot, port: int=8000):
		"""
		Parameters:
			bot: The Discord bot
			port: The port for the Prometheus server
		"""

		self.bot = bot
		self.port = port

		self.started = False

	@commands.Cog.listener()
	async def on_ready(self):

		# some gauges needs to be initialized after each reconect
		# (value could changed during an outtage)
		self.init_gauges()

		# Set connection back up (since we in on_ready)
		CONNECTION_GAUGE.set(1)

		# on_ready can be called multiple times, this started
		# check is to make sure the service does not start twice
		if not self.started:
			self.start_prometheus()

	def init_gauges(self):
		log.info('Initializing gauges')

		num_of_guilds = len(self.bot.guilds)
		GUILD_GAUGE.set(num_of_guilds)

		num_of_channels = len(set(self.bot.get_all_channels()))
		CHANNEL_GAUGE.set(num_of_channels)

		num_of_users = len(set(self.bot.get_all_members()))
		USER_GAUGE.set(num_of_users)

		num_of_commands = len(self.get_all_commands())
		COMMANDS_GAUGE.set(num_of_commands)

	def get_all_commands(self):
		return [
			*self.bot.walk_commands(),
			*self.bot.tree.walk_commands()
		]

	def start_prometheus(self):
		log.info(f'Starting Prometheus Server on port {self.port}')
		start_http_server(self.port)
		self.started = True

	@commands.Cog.listener()
	async def on_command(self, ctx: commands.Context):
		ON_COMMAND_COUNTER.labels(ctx.command.name).inc()

	@commands.Cog.listener()
	async def on_interaction(self, interaction: Interaction):
		# command name can be None if comming from a view (like a button click)
		name = None

		if interaction.type == InteractionType.application_command:
			name = interaction.command.name
		elif interaction.type == InteractionType.autocomplete:
			name = 'autocomplete'
		elif interaction.type == InteractionType.component:
			name = 'component'
		elif interaction.type == InteractionType.modal_submit:
			name = 'modalSubmit'

		ON_INTERACTION_COUNTER.labels(name).inc()

	@commands.Cog.listener()
	async def on_connect(self):
		CONNECTION_GAUGE.set(1)

	@commands.Cog.listener()
	async def on_resumed(self):
		CONNECTION_GAUGE.set(1)

	@commands.Cog.listener()
	async def on_disconnect(self):
		CONNECTION_GAUGE.set(0)

	@commands.Cog.listener()
	async def on_guild_join(self, _):
		# The number of guilds, channels and users needs to be updated all together
		self.init_gauges()

	@commands.Cog.listener()
	async def on_guild_remove(self, _):
		# The number of guilds, channels and users needs to be updated all together
		self.init_gauges()

	@commands.Cog.listener()
	async def on_guild_channel_create(self, _):
		CHANNEL_GAUGE.inc()

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, _):
		CHANNEL_GAUGE.dec()

	@commands.Cog.listener()
	async def on_member_join(self, _):
		USER_GAUGE.inc()

	@commands.Cog.listener()
	async def on_member_remove(self, _):
		USER_GAUGE.dec()
