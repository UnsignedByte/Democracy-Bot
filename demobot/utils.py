from discord import VoiceRegion, Forbidden, DMChannel
import datetime
from pytz import timezone
import pytz
import itertools
import asyncio
from random import shuffle
from collections import OrderedDict
from demobot.handlers import nested_get

def format_response(string, **kwargs):
    if "_msg" in kwargs:
        message = kwargs["_msg"]
        kwargs["_msgcontent"] = message.content
        kwargs["_author"] = message.author
    if "_author" in kwargs:
        author = kwargs["_author"]
        kwargs["_name"] = author.display_name
        kwargs["_username"] = author.name
        kwargs["_mention"] = author.mention

    return string.format(**kwargs)

async def is_official(u, canenf=True):
    roles = nested_get(u.guild.id, "roles")
    print(get_official(u))
    return bool(len(get_official(u)) - (0 if canenf or roles['enforcer'] not in u.roles else 1))

async def get_official(u):
    govs = ['judge', 'representative', 'leader', 'enforcer']
    roles = nested_get(u.guild.id, "roles")
    return [r for r in govs if roles[r] in u.roles]

async def get_owner(Demobot):
    return (await Demobot.application_info()).owner

async def govPos(Demobot, user, role, canEnf=True):
    await user.send_message("You have been offered the "+role.name+" position in government. Would you like to accept the offer?")
    if is_official(user, canenf=canEnf):
        await user.send_message("You will lose the following positions: "+', '.join(map(lambda x:x.name, get_official(user))))
    def check(msg):
        return True
    await Demobot.wait_for('message', check=check)
    await user.add_roles(role)

def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class Votes:
    def __init__(self):
        self.up = 0
        self.none = 0
        self.down = 0


class Proposal:
    def __init__(self, msg, tt, content, author):
        self.msg = msg
        self.votes = Votes()
        self.voted = []
        self.tt = tt
        self.content = content
        self.author = author

    def __eq__(self, a):
        return self.msg == a.msg

class Nomination(Proposal):
    def __init__(self, msg, tt, content, author, usr, role):
        Proposal.__init__(self, msg, tt, content, author)
        self.usr = usr
        self.role=role

class Candidate:
    def __init__(self, desc, ii):
        self.desc = desc
        self.ii = ii
        self.up = set([])
        self.down = set([])


class Backup:
    def __init__(self, time, score):
        self.time = time
        self.score = score
