# Travis Weir
# 12/7/17
# SnuWumpus

import json, os.path, sys, praw, discord, asyncio, datetime
from discord.ext.commands import Bot

config = {
    'prefix': '^',
    'reddit_username': "Put Reddit account username here.",
    'reddit_password': "Put the password for your Reddit account here",
    'reddit_secret': "Reddit client secret goes here",
    'reddit_clientid': "Reddit client ID goes here",
    'discord_token': "Put Discord API Token here.",
    'reddit_channel': "Put the ID of the channel you want to send Reddit messages to here.",
    'submissionstream_channel': "Put the ID of the channel you want the subreddit scraper to send in here",
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

ackmessages = []

try:
    submissionstreamlist = open('submissionstream.txt', mode='r')
except FileNotFoundError:
    open('submissionstream.txt', mode='x')
    submissionstreamlist = open('submissionstream.txt', mode='a+')

processedsubmissions = []

for i in submissionstreamlist.readlines():
    i = i.strip('\n')
    processedsubmissions.append(i)
submissionstreamlist.close()


@discordbot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send('Author must be specified!')


async def inboxcheck():
    for i in reddit.inbox.unread():
        if i is not None and i not in ackmessages:
            embed = discord.Embed(type='rich')
            embed.add_field(name="Author", value=i.author)
            embed.add_field(name="Subject", value=i.subject, inline=False)
            embed.add_field(name="Message body", value=i.body, inline=False)
            creation_time = datetime.datetime.fromtimestamp(i.created_utc)
            embed.add_field(name="Time", value="{} in UTC".format(creation_time))
            sendto = Bot.get_channel(self=discordbot, id=int(config['reddit_channel']))
            ackmessages.append(i)
            await sendto.send(embed=embed)


async def subredditscraper():
    subreddit = reddit.subreddit('frcredditscrapertest')
    for i in subreddit.stream.submissions():
        if i not in processedsubmissions:
            with open('submissionstream.txt', mode='a') as submissionstreamlist:
                submissionstreamlist.write("\n{}".format(i.id))
            e = discord.Embed(type='rich')
            e.title = "New submission in /r/FRC"
            e.add_field(name='Author', value=i.author)
            e.add_field(name='Title', value=i.title)
            if 1024 > len(i.selftext) > 0:
                e.add_field(name='Body', value=i.selftext, inline=False)
            if len(i.selftext) > 1024:
                text = i.selftext
                while len(text) != 0:
                    e.add_field(name="Body", value=text[0:1023])
                    text = text[1023:]
            channel = discordbot.get_channel(id=int(config['submissionstream_channel']))
            await channel.send(embed=e)
            await channel.send("Link: {}".format(i.url))


@discordbot.command()
async def approve(ctx, author):
    for i in reddit.inbox.unread():
        if str(i.author) == str(author):
            invite = str(await discord.Client.get_channel(self=ctx.bot, id=int(config['invite_channel'])).create_invite(max_uses=1))
            i.author.message(subject='FRC Discord invite', message="Congratulations! You've been accepted into the FRC Discord"
                                                                   " server. Here's your invite: {}".format(invite))
            i.mark_read()
            await ctx.send("Invite sent")
            break


@discordbot.command()
async def deny(ctx, author):
    for i in reddit.inbox.unread():
        if str(i.author) == str(reddit.redditor(author)):
            i.author.message(subject='FRC Discord invite', message="Sorry, but the moderation team has decided to deny"
                                                                   " you at this time.")
            i.mark_read()
            await ctx.send("Message sent")
            break


@discordbot.command()
async def ignore(ctx, author):
    for i in reddit.inbox.unread():
        if str(i.author) == str(reddit.redditor(author)):
            i.mark_read()
            await ctx.send("Ignored user")
            break


async def timing():
    while True:
        await inboxcheck()
        await subredditscraper()
        await asyncio.sleep(300)


@discordbot.event
async def on_ready():
    print('ready')
    await timing()


discordbot.run(config['discord_token'])
