import asyncio
import pickle
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data
from discord import Embed

@asyncio.coroutine
def save(Discow, msg, reg, overrideperms = False):
    if overrideperms or msg.author.id in ["418827664304898048", "418667403396775936"]:
        if not overrideperms:
            em = Embed(title="Saving Data...", description="Saving...", colour=0xd32323)
            msg = yield from send_embed(Discow, msg, em)
            yield from asyncio.sleep(1)
        data = get_data()
        with open("data/settings.txt", "wb") as f:
            pickle.dump(data[0], f)
        if not overrideperms:
            em.description = "Complete!"
            msg = yield from edit_embed(Discow, msg, embed=em)
            yield from asyncio.sleep(0.5)
            yield from Discow.delete_message(msg)
        return True
    else:
        em = Embed(title="Insufficient Permissions", description=format_response("{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        yield from send_embed(Discow, msg, em)
        return False

add_message_handler(save, r'^save')
