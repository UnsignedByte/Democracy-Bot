from discord import ServerRegion, Forbidden
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


def parse_command(msg, num=-1):
    cont = msg[len(demobot_prefix):].split(" ")
    if num is not -1:
        if len(cont)<num+1:
            raise IndexError("Not enough inputs")
        else:
            return cont[:num]+[' '.join(cont[num:])]
    else:
        return cont


def strip_command(msg):
    return parse_command(msg, 1)[1]


def convertTime(time, msg):
    if msg.channel.is_private:
        zone = timezone("Europe/London")
    else:
        timezones = {
            ServerRegion.us_west:"America/Los_Angeles",
            ServerRegion.us_east:"America/New_York",
            ServerRegion.us_central:"US/Central",
            ServerRegion.eu_west:"Europe/Amsterdam",
            ServerRegion.eu_central:"Europe/Berlin",
            ServerRegion.singapore:"Singapore",
            ServerRegion.london:"Europe/London",
            ServerRegion.sydney:"Australia/Sydney",
            ServerRegion.amsterdam:"Europe/Amsterdam",
            ServerRegion.frankfurt:"Europe/Berlin",
            ServerRegion.brazil:"Brazil/Acre",
            ServerRegion.vip_us_east:"America/New_York",
            ServerRegion.vip_us_west:"America/Los_Angeles",
            ServerRegion.vip_amsterdam:"Europe/Amsterdam",
            'russia':'Europe/Russia'
        }
        zone = timezone(timezones[msg.server.region])
    time_naive = time.replace(tzinfo=pytz.utc)
    loctime = time_naive.astimezone(zone)
    fmt = '%Y-%m-%d at %H:%M:%S %Z'
    return loctime.strftime(fmt)


def nickname(usr, srv):
    if not srv:
        return usr.name
    n = srv.get_member(usr.id).nick
    if not n:
        return usr.name
    return n

async def send_embed(Discow, msg, embed, time=datetime.datetime.utcnow(), usr=None):
    if not usr:
        usr = Discow.user
    txt = "Created by "+nickname(usr, msg.server)+" on "+convertTime(time, msg)+"."
    embed.set_footer(text=txt, icon_url=(usr.avatar_url if usr.avatar_url else usr.default_avatar_url))
    try:
        m = await Discow.send_message(msg.channel, embed=embed)
        return m
    except Forbidden:
        await Discow.send_message(msg.channel,
                                       "**Missing Permissions**\nDiscow is missing permissions to perform this task.")
        return None


async def edit_embed(Discow, msg, embed, time=datetime.datetime.utcnow(), usr=None):
    if not usr:
        usr = Discow.user
    txt = "Edited by "+nickname(usr, msg.server)+" on "+convertTime(time, msg)+"."
    embed.set_footer(text=txt, icon_url=(usr.avatar_url if usr.avatar_url else usr.default_avatar_url))
    m = await Discow.edit_message(msg, embed=embed)
    return m

async def is_official(u, canenf=True):
    roles = nested_get(u.server.id, "roles")
    print(get_official(u))
    return bool(len(get_official(u)) - (0 if canenf or roles['enforcer'] not in u.roles else 1))

async def get_official(u, getenf=True):
    govs = ['judge', 'representative', 'leader'] + (['enforcer'] if getenf else [])
    roles = nested_get(u.server.id, "roles")
    return [roles[r] for r in govs if roles[r] in u.roles]

async def get_owner(Demobot):
    return (await Demobot.application_info()).owner

async def govPos(Demobot, user, role, canEnf=True):
    m = await Demobot.send_message(user, "You have been offered the "+role.name+" position in government. Would you like to accept the offer?")
    p = await get_official(user, not canEnf)
    if role in p:
        p.remove(role)
    if p:
        await Demobot.send_message(user, "You will lose the following positions: "+', '.join(map(lambda x:x.name, p)))
    def check(s):
        return s.content.lower() in ['yes', 'no', 'y', 'n']
    m2 = await Demobot.wait_for_message(timeout=600, author=user, channel=m.channel, check=check)
    if m2 and m2.content.lower() in ['yes', 'y']:
        await Demobot.add_roles(user, role)
        await Demobot.remove_roles(user, *p)
        return True
    else:
        return False

def is_citizen(user):
    return nested_get(user.server.id, 'roles', 'citizen') in user.roles

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
