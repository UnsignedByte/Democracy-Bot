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
                for j in deepcopy(list(demobot.handlers.nested_get(a, 'messages', 'proposals').values())):
                    self.messages.append(j.msg)
        await self.change_presence(activity=discord.Activity(name='The Democracy', type=discord.ActivityType.watching, state='Watching'), status=discord.Status.online)
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
        #await demobot.handlers.on_reaction_add(self, reaction, user)
        return
    async def on_raw_reaction_add(self, payload):
        print(payload)
        m = await self.get_channel(payload.channel_id).get_message(payload.message_id)
        x = discord.utils.get(m.reactions, emoji=payload.emoji)
        await demobot.handlers.on_reaction_add(self, x, m.guild.get_member(payload.user_id))
    async def on_reaction_remove(self, reaction, user):
        await demobot.handlers.on_reaction_delete(self, reaction, user)
Demobot = DemocracyClient()


def runBot():
    Demobot.run(_getkey.key())


if __name__ == "__main__":
    print("Auth key is %s" % _getkey.key())
