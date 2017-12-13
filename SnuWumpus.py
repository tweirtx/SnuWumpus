# Travis Weir
# 12/7/17
# SnuWumpus

import json, os.path, sys, praw, discord, asyncio
from discord.ext.commands import Bot

config = {
    'prefix': '^', 'developers': [],
    'reddit_username': "Put Reddit account username here.",
    'reddit_password': "Put the password for your Reddit account here",
    'reddit_secret': "Reddit client secret goes here",
    'reddit_clientid': "Reddit client ID goes here",
    'discord_token': "Put Discord API Token here.",
    'reddit_channel': "Put the ID of the channel you want to send Reddit messages to here."
}
config_file = 'config.json'

if os.path.isfile(config_file):
    with open(config_file) as f:
        config.update(json.load(f))

with open('config.json', 'w') as f:
    json.dump(config, f, indent='\t')

if 'discord_token' not in config:
    sys.exit('Discord token must be supplied in configuration')

reddit = praw.Reddit(client_id=config['reddit_clientid'],    #Log in to Reddit
                     client_secret=config['reddit_secret'], password=config['reddit_password'],  #Log in to Reddit
                     user_agent='FRC Discord Reddit Invitation Manager by Travis', username=config['reddit_username'])

discordbot = Bot(command_prefix=config['prefix'])


async def inboxcheck():
    for i in reddit.inbox.unread():
        if i is not None:
            embed = discord.Embed(type='rich')
            embed.add_field(name="Author", value=i.author)
            embed.add_field(name="Subject", value=i.subject)
            embed.add_field(name="Message body", value=i.body)
            sendto = discordbot.get_channel(config['reddit_channel'])
            print(sendto)
            sendto.send(embed=embed)


@discordbot.command
async def approve(author):
    for i in reddit.inbox.unread:
        if i.author == reddit.redditor(author):
            invite = await discordbot.get_guild(id=discordbot.guilds[0]).create_invite(xkcd=True, max_uses=1)
            i.author.message("Congratulations! You've been accepted into the FRC Discord server. Here's your invite: {}".format(invite))
            i.mark_read()
            break


async def timing():
    await inboxcheck()
    await asyncio.sleep(300)


@discordbot.event
async def on_ready():
    print('ready')
    await timing()


discordbot.run(config['discord_token'])
