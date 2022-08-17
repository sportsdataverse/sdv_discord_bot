import os
import discord
from discord.ext import commands

# load bot token
token = os.environ.get('DISCORD_TOKEN')

# declare intents
intents = discord.Intents.all()
client = commands.Bot(command_prefix='?', intents=intents)

# assign role ids
sdv_team = 821195094639247390
unverified = 1008955473225072661

@client.event
async def on_read():
    print('We have logged in as {0.user}'.format(client))

# assign an unverified role when someone joins the server
@client.event
async def on_member_join(member):
    unveri = discord.utils.get(member.guild.roles, id=int(unverified))
    await member.add_roles(unveri)
    # send a message to the channel when a member joins
    channel = discord.utils.get(member.guild.channels, name='introduce-yoself')
    await channel.send(f'{member.mention}, welcome! To access the server, please verify yourself by sending a quick introduction while mentioning who invited you. This message will soon self-destruct.', delete_after=30)

# assign a role to a user when they send their first message
@client.event
async def on_message(message):
    # only check in the welcome channel and ignore messages from bots
    if message.channel.name == 'introduce-yoself' and message.author != client.user:
        author = message.author
        # if user does not have the sdv-role assign them the role and remove the unverified role
        if not discord.utils.get(message.author.roles, name='sdv-team'):
            # add sdv-team role
            sdv = discord.utils.get(message.guild.roles, id=int(sdv_team))
            await author.add_roles(sdv)
            # remove unverified role
            unveri = discord.utils.get(message.guild.roles, id=int(unverified))
            await author.remove_roles(unveri)
            # welcome the member
            channel = discord.utils.get(author.guild.channels, name='introduce-yoself')
            await channel.send(f'Welcome, {author.mention}! You are now free to explore the SDV server! We are excited to have you here.', delete_after=30)

client.run('DISCORD_TOKEN')