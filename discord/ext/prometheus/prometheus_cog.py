import logging
from typing import Optional, Iterable

from discord import Interaction, InteractionType, AutoShardedClient
from discord.ext import commands, tasks
from prometheus_client import start_http_server, Gauge, CollectorRegistry

logger = logging.getLogger(__name__)


class PrometheusCog(commands.Cog):
	"""
	A Cog to be added to a discord bot. The prometheus server will start once the bot is ready
	using the `on_ready` listener.
	"""
	METRIC_PREFIX = "discord_"

	def __init__(
		self,
		bot: commands.Bot,
		*,
		run_server: bool = True,
		port: int = 8000,
		registry: Optional[CollectorRegistry] = None,
	) -> None:
		"""
		Parameters:
			bot: The Discord bot
			run_server: If the Prometheus server should be started
			port: The port for the Prometheus server
		"""

		self.bot = bot
		self.port = port

		self.should_run = run_server

		self.registry = registry or CollectorRegistry()
		self.metrics = {}

		self.init_gauges()

	def _m(
		self,
		name: str,
		*,
		documentation: Optional[str] = None,
		labels: Optional[Iterable[str]] = None
	) -> Gauge:
		"""Get a metric from the registry, creating it if it does not exist."""
		documentation = documentation or name
		if name not in self.metrics:
			self.metrics[name] = Gauge(
				self.METRIC_PREFIX + name,
				documentation,
				registry=self.registry,
				labelnames=labels or (),
			)
		return self.metrics[name]

	def init_gauges(self):
		self._m(
			"connected",
			documentation="Connection status to Discord",
			labels=("shard",),
		)
		self._m(
			"errors",
			documentation="Amount of errors",
		)
		self._m(
			"latency",
			documentation="Websocket latency to Discord",
			labels=("shard",),
		)
		self._m(
			"event_on_interaction",
			documentation="Amount of interactions called by users",
			labels=("shard", "interaction", "command"),
		)
		self._m(
			"event_on_command",
			documentation="Amount of commands called by users",
			labels=("shard", "command"),
		)
		stat_total_guilds = self._m(
			"stat_total_guilds",
			documentation="Amount of guild this bot is a member of",
		)
		stat_total_guilds.set_function(lambda: len(self.bot.guilds))
		stat_total_channels = self._m(
			"stat_total_channels",
			documentation="Amount of channels this bot is has access to",
		)
		stat_total_channels.set_function(lambda: len((*self.bot.get_all_channels(),)))
		stat_total_users = self._m(
			"stat_total_users",
			documentation="Amount of users this bot can see",
		)
		stat_total_users.set_function(lambda: len(self.bot.users))
		stat_total_members = self._m(
			"stat_total_members",
			documentation="Amount of members this bot can see",
		)
		stat_total_members.set_function(lambda: len((*self.bot.get_all_members(),)))
		stat_total_commands = self._m(
			"stat_total_commands",
			documentation="Amount of commands this bot has",
		)
		stat_total_commands.set_function(lambda: len((*self.bot.walk_commands(),)))

	async def cog_load(self) -> None:
		self.latency_loop.start()
		if self.should_run:
			start_http_server(self.port, registry=self.registry)

	async def cog_unload(self) -> None:
		self.latency_loop.cancel()

	def collect(self):
		for _ in self.registry.collect():
			pass

	@tasks.loop(seconds=5)
	async def latency_loop(self):
		if isinstance(self.bot, AutoShardedClient):
			for shard, latency in self.bot.latencies:
				self._m("latency").labels(shard).set(latency)
		else:
			self._m("latency").labels(None).set(self.bot.latency)

	@commands.Cog.listener()
	async def on_ready(self):
		self.collect()

	@commands.Cog.listener()
	async def on_command(self, ctx: commands.Context):
		shard_id = ctx.guild.shard_id if ctx.guild else None
		self._m("event_on_command").labels(shard_id, ctx.command.name).inc()

	@commands.Cog.listener()
	async def on_interaction(self, interaction: Interaction):

		shard_id = interaction.guild.shard_id if interaction.guild else None

		# command name can be None if comming from a view (like a button click) or a modal
		command_name = None
		if interaction.type == InteractionType.application_command and interaction.command:
			command_name = interaction.command.name

		self._m("event_on_interaction").labels(shard_id, interaction.type.name, command_name).inc()

	# Connection events

	@commands.Cog.listener()
	async def on_connect(self):
		self._m("connected").labels(None).set(1)

	@commands.Cog.listener()
	async def on_resumed(self):
		self._m("connected").labels(None).set(1)

	@commands.Cog.listener()
	async def on_disconnect(self):
		self._m("connected").labels(None).set(0)

	@commands.Cog.listener()
	async def on_shard_ready(self, shard_id):
		self._m("connected").labels(shard_id).set(1)

	@commands.Cog.listener()
	async def on_shard_connect(self, shard_id):
		self._m("connected").labels(shard_id).set(1)

	@commands.Cog.listener()
	async def on_shard_resumed(self, shard_id):
		self._m("connected").labels(shard_id).set(1)

	@commands.Cog.listener()
	async def on_shard_disconnect(self, shard_id):
		self._m("connected").labels(shard_id).set(0)

	# Collector cues

	@commands.Cog.listener()
	async def on_guild_join(self, _):
		self.collect()

	@commands.Cog.listener()
	async def on_guild_remove(self, _):
		self.collect()

	@commands.Cog.listener()
	async def on_guild_channel_create(self, _):
		self.collect()

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, _):
		self.collect()

	@commands.Cog.listener()
	async def on_member_join(self, _):
		self.collect()

	@commands.Cog.listener()
	async def on_member_remove(self, _):
		self.collect()


__all__ = ("PrometheusCog",)
