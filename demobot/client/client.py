import discord
import asyncio
import logging
import datetime
from pprint import pprint
from copy import deepcopy

import demobot.client.getkey as _getkey
import demobot.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='data/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class DemocracyClient(discord.Client):
    async def on_ready(self):
        for a in demobot.handlers.server_data:
            propchan = demobot.handlers.nested_get(a, "channels", "proposals")
            if propchan:
                for j in deepcopy(demobot.handlers.nested_get(a, "proposals", "messages")):
                    t = j.msg.edited_timestamp
                    t = t if t else j.msg.timestamp
                    if (datetime.datetime.utcnow() - t).total_seconds() > 1:
                        demobot.handlers.nested_remove(j, a, "proposals", "messages",
                                                       func=lambda x, y: x.msg.id == y.msg.id)
                    else:
                        self.messages.append(j)
        await self.change_presence(game=discord.Game(name='Nichodon\'s Tester', type=3))
        await asyncio.gather(demobot.handlers.elections_timed(self), demobot.handlers.minutely_check(self))

    async def on_message(self, message):
        await demobot.handlers.on_message(self, message)

    async def on_message_edit(self, before, after):
        await demobot.handlers.on_message(self, after)

    async def on_member_update(self, before, after):
        await demobot.handlers.member_update(self, before, after)

    async def on_member_join(self, member):
        await demobot.handlers.newuser(self, member)

    async def on_reaction_add(self, reaction, user):
        await demobot.handlers.on_reaction_add(self, reaction, user)

    async def on_reaction_remove(self, reaction, user):
        await demobot.handlers.on_reaction_delete(self, reaction, user)


Demobot = DemocracyClient()


def runBot():
    Demobot.run(_getkey.key())


if __name__ == "__main__":
    print("Auth key is %s" % _getkey.key())
