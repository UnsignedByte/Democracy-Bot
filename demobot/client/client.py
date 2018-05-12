import discord
import asyncio
import logging

import demobot.client.getkey as _getkey
import demobot.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='data/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class DemocracyClient(discord.Client):
    async def on_ready(self):
        await self.change_presence(game=discord.Game(name='The Democracy', url='https://github.com/UnsignedByte/Democracy-Bot', type=1))
        await demobot.handlers.timed_message(self)

    async def on_message(self, message):
        await demobot.handlers.on_message(self, message)


Demobot = DemocracyClient()


def runBot():
    Demobot.run(_getkey.key())


if __name__ == "__main__":
    print("Auth key is %s" % _getkey.key())
