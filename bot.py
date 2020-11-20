import os
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

#loads values that are needed and values which should be kept private
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BEDWARS = os.getenv("DISCORD_BEDWARS")
BIRTHDAY = os.getenv("DISCORD_BIRTHDAY")
AUTHORIZATION = os.getenv("TWITCH_AUTHORIZATION")
CLIENTID = os.getenv("TWITCH_CLIENT")
USERID = os.getenv("USER_ID")
NOTIF_ROLE = os.getenv("NOTIF_ROLE")
NOTIF_CHANNEL = os.getenc("NOTIF_CHANNEL")

intents = discord.Intents.default()
intents.members = True

#specifies to run a bot command with .
client =  commands.Bot(command_prefix='.', intents=intents)

#sets up values needed to connect to the twitch API
headers = {
    'client-id': CLIENTID,
    'Authorization': AUTHORIZATION,
}
url ="https://api.twitch.tv/helix/streams"
params = {
    "user_id": USERID
}


# runs when bot first starts, lists all servers it connected to
@client.event
async def on_ready():
    for guild in client.guilds:
        print(
        f'{client.user} has connected to this server:\n'
        f'{guild}(id: {guild.id})')
    #starts background task that runs to periodically check if a specified twitch channel is live
    client.bg_task = client.loop.create_task(channel_check())
    
#Sends message to server and privately messages someone when they join server
#@client.event
#async def on_member_join(member):
    #guild = member.guild
    #await member.send('Pssst you should check out this streamer https://www.twitch.tv/krypticphox')
    #if guild.system_channel is not None:
        #to_send = "Hey {0.mention}, you should check out this cool streamer https://www.twitch.tv/krypticphox".format(member)
        #await guild.system_channel.send(to_send)

#responds with the person who wrote the commands latency
@client.command()
async def ping(ctx):
    await ctx.send(f"{ctx.author} ping is {round(client.latency*1000)}ms")

#Helper function which alternates capitalization and decapitalization
def automeme(string):
    for int in range(len(string)):
        temp = string[int]
        if (int%2 == 1):
            string = string[:int] + temp.capitalize() + string[int+1:]
        else:
            string = string[:int] + temp.lower() + string[int+1:]
    return string


#gets last message on channel and sends it back after running through automeme
@client.command()
async def meme(ctx):
    channel = ctx.channel
    messages = await channel.history(limit=2).flatten()
    await ctx.send(f"{automeme(messages[1].content)}")


#sends link to twitch channel
@client.command()
async def link(ctx):
    await ctx.send(f"https://www.twitch.tv/krypticphox")

#pings all members listed in BEDWARS
@client.command()
async def bedwars(ctx):
    await ctx.send(f"BEDWARS NOW {BEDWARS}")

#Sends birthday message to whoever is referenced in BIRTHDAY
@client.command()
async def birfday(ctx):
    await ctx.send(f"Hey {BIRTHDAY} we at the phoxbot company wish you a happy birthday \n https://www.youtube.com/watch?v=ho08YLYDM88")


#Background task which checks if specified twitch channel is live, if it is check if it has been announced,
#  if it hasn't been announce it and set announce to True, if it has been announced check back in 60 seconds
#   If channel is not live set announce to False and check back in 60 seconds
async def channel_check():
    announce = False
    while True:
        response = requests.get(url, headers=headers,params=params)
        if(not (response.text[8:10]=="[]")):
            if announce == False:
                channel = client.get_channel(NOTIF_CHANNEL)
                await channel.send(f"{NOTIF_ROLE} KrypticPhox is live https://www.twitch.tv/krypticphox ")
                announce = True
        else: announce = False
        await asyncio.sleep(60)


#runs bot
client.run(TOKEN)



