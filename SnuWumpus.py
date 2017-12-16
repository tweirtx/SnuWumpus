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
    'reddit_channel': "Put the ID of the channel you want to send Reddit messages to here.",
    'invite_channel': "Put the ID of the channel you want to invite users to here."
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
            sendto = discordbot.get_channel(int(config['reddit_channel']))
            await sendto.send(embed=embed)


@discordbot.command()
async def approve(ctx, author="No author"):
    if author == "No author":
        await ctx.send("Please specify an author!")
    for i in reddit.inbox.unread():
        if str(i.author) == str(reddit.redditor(author)):
            invite = str(await discord.Client.get_channel(self=ctx.bot, id=int(config['invite_channel'])).create_invite(max_uses=1))
            i.author.message(subject='FRC Discord invite', message="Congratulations! You've been accepted into the FRC Discord "
                                                                   "server. Here's your invite: {}".format(invite))
            i.mark_read()
            await ctx.send("Invite sent")
            break


@discordbot.command()
async def deny(ctx, author="No author"):
    if author == "No author":
        await ctx.send("Please specify an author!")
    for i in reddit.inbox.unread():
        if str(i.author) == str(reddit.redditor(author)):
            i.author.message(subject='FRC Discord invite', message="Sorry, but the moderation team has decided to deny"
                                                                   " you at this time.")
            i.mark_read()
            await ctx.send("Message sent")
            break


@discordbot.command()
async def ignore(ctx, author="No author"):
    if author == "No author":
        await ctx.send("Please specify an author!")
    for i in reddit.inbox.unread():
        if str(i.author) == str(reddit.redditor(author)):
            i.mark_read()
            await ctx.send("Ignored user")
            break


async def timing():
    while True:
        await inboxcheck()
        await asyncio.sleep(300)


@discordbot.event
async def on_ready():
    print('ready')
    await timing()


discordbot.run(config['discord_token'])
