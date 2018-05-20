import asyncio
import pickle
from demobot.utils import *
from demobot.handlers import add_message_handler, get_data
from discord import Embed


async def save(Demobot, msg, reg, overrideperms=False):
    if overrideperms or msg.author.id in ["418827664304898048"]:
        if not overrideperms:
            em = Embed(title="Saving Data...", description="Saving...", colour=0xd32323)
            msg = await send_embed(Demobot, msg, em)
            await asyncio.sleep(1)
        data = get_data()
        with open("data/settings.txt", "wb") as f:
            pickle.dump(data[0], f)
        if not overrideperms:
            em.description = "Complete!"
            msg = await edit_embed(Demobot, msg, embed=em)
            await asyncio.sleep(0.5)
            await Demobot.delete_message(msg)
        return True
    else:
        em = Embed(title="Insufficient Permissions", description=format_response(
            "{_mention} does not have sufficient permissions to perform this task.", _msg=msg), colour=0xd32323)
        await send_embed(Demobot, msg, em)
        return False

add_message_handler(save, r'^save')
