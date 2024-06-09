
# discord-ext-prometheus

![PyPI Version](https://img.shields.io/pypi/v/discord-ext-prometheus.svg)
![PyPI Python Version](https://img.shields.io/pypi/pyversions/discord-ext-prometheus.svg?logo=python&logoColor=gold)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![License MIT](https://img.shields.io/pypi/l/discord-ext-prometheus)
![Grafana Dashboard Downloads](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fgrafana.com%2Fapi%2Fdashboards%2F17670&query=%24.downloads&logo=Grafana&label=downloads&color=orange)

This is a library that makes it easy to add prometheus metrics to your Python Discord bot.

# Installation

```bash
pip install discord-ext-prometheus
```

# Exposed Metrics

| Name                           | Documentation                                 | Labels                            |
|--------------------------------|-----------------------------------------------|-----------------------------------|
| `discord_connected`            | Determines if the bot is connected to Discord | `shard`                           |
| `discord_latency`              | Latency to Discord                            | `shard`                           |
| `discord_event_on_interaction` | Amount of interactions called by users        | `shard`, `interaction`, `command` |
| `discord_event_on_command`     | Amount of commands called by users            | `shard`, `command`                |
| `discord_stat_total_guilds`    | Amount of guild this bot is a member of       | None                              |
| `discord_stat_total_channels`  | Amount of channels this bot is has access to  | None                              |
| `discord_stat_total_users`     | Amount of users this bot can see              | None                              |
| `discord_stat_total_commands`  | Amount of commands                            | None                              |
| `logging`                      | Log entries                                   | `logger`, `level`                 |

Notes:
- `on_interaction` are application interactions such as slash commands or modals
- `on_command` are traditional message commands (usualy using the command prefix)

# Grafana Dashboard

![Dashboard Preview](https://grafana.com/api/dashboards/17670/images/13525/image)

Available to import from [Grafana dashboards](https://grafana.com/grafana/dashboards/17670-discord-bot/)

# How to use

Once the cog is added to your bot, the Prometheus metric endpoint can be accessed
at `localhost:8000/metrics`.

## Sample code with the Prometheus Cog

```python
import asyncio
from discord import Intents
from discord.ext import commands
from discord.ext.prometheus import PrometheusCog

async def main():
	bot = commands.Bot(
		command_prefix='!',
		intents=Intents.all(),
	)

	await bot.add_cog(PrometheusCog(bot))

	await bot.start('YOUR TOKEN')

asyncio.run(main())
```

## Sample code with logging metrics

```python
import asyncio
import logging
from discord import Intents
from discord.ext import commands
from discord.ext.prometheus import PrometheusCog, PrometheusLoggingHandler

logging.getLogger().addHandler(PrometheusLoggingHandler())

async def main():
	bot = commands.Bot(
		command_prefix='!',
		intents=Intents.all(),
	)

	await bot.add_cog(PrometheusCog(bot))

	@bot.listen()
	async def on_ready():
		logging.info(f'Logged in as {bot.user.name}#{bot.user.discriminator}')

	logging.info('Starting the bot')
	await bot.start('YOUR TOKEN')

asyncio.run(main())
```

## Change the Prometheus port

The default port is `8000` but can be changed while creating the cog.

```python
await bot.add_cog(PrometheusCog(bot, port=7000))
```
