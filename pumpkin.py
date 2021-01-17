import os
import sys
import logging
import logging.config

import discord
from discord.ext import commands

logging.config.fileConfig("core/log.conf")
logger = logging.getLogger("pumpkin_log")

# Setup checks


def test_dotenv() -> None:
    if type(os.getenv("DB_STRING")) != str:
        logger.critical("DB_STRING is not set.")
        sys.exit(1)
    if type(os.getenv("TOKEN")) != str:
        logger.critical("TOKEN is not set.")
        sys.exit(1)
    if type(os.getenv("BOT_PREFIX")) != str:
        logger.critical("BOT_PREFIX is not set.")
        sys.exit(1)
    if os.getenv("BOT_MENTIONPREFIX") not in ("0", "1"):
        logger.critical("BOT_MENTIONPREFIX has to be '0' or '1'.")
        sys.exit(1)
    if type(os.getenv("BOT_LANGUAGE")) != str:
        logger.critical("BOT_LANGUAGE is not set.")
        sys.exit(1)
    if os.getenv("BOT_GENDER") not in ("m", "f"):
        logger.critical("BOT_GENDER has to be 'm' or 'f'.")
        sys.exit(1)


test_dotenv()


# Setup discord.py


def get_prefix() -> str:
    """Get bot prefix with optional mention function"""
    if os.getenv("BOT_MENTIONPREFIX") == "1":
        return commands.when_mentioned_or(os.getenv("BOT_PREFIX"))
    return os.getenv("BOT_PREFIX")


intents = discord.Intents.default()
intents.members = True


bot = commands.Bot(
    command_prefix=get_prefix(),
    allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
    intents=intents,
)


# Setup listeners


@bot.event
async def on_ready():
    """If bot is ready."""
    logger.info("The pie is ready.")


@bot.event
async def on_error(event, *args, **kwargs):
    logger.exception("Unhandled exception")


# Add required modules


modules = (
    "base.base",
    "base.errors",
    "base.admin",
)

for module in modules:
    bot.load_extension("modules." + module)
    logger.info("Loaded " + module)


# Run the bot


bot.run(os.getenv("TOKEN"))
