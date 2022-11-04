import os
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import openai

#loads values that are needed and values  which should be kept private
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHORIZATION = os.getenv("TWITCH_AUTHORIZATION")
CLIENTID = os.getenv("TWITCH_CLIENT")
USERID = os.getenv("USER_ID")
NOTIF_ROLE = os.getenv("NOTIF_ROLE")
NOTIF_CHANNEL = os.getenv("NOTIF_CHANNEL")
OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.members = True
intents.message_content=True

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

def islive():
    response = requests.get(url, headers=headers,params=params)
    if(not (response.text[8:10]=="[]")):
        return True

def gpthelper(key,message):
    openai.api_key = key
    MAX_TOKENS = 4000
    text_input = message
    remaining = MAX_TOKENS - len(text_input)
    if remaining < 0:
        return "Prompt too long"

    try:
        response = openai.Completion.create(
        model="text-davinci-002",
        prompt=text_input,
        temperature=0.5,
        max_tokens=remaining,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
    except openai.error.RateLimitError:
        return "sending requests too quickly"
    else:
        #print(f"Response will be max {remaining} character length")
        return response["choices"][0]["text"]

@client.command()
async def gpt(ctx):
    channel = ctx.channel
    messages = ctx.message.content.split(".gpt")[1]
    await ctx.send(f"{gpthelper(OPEN_AI_KEY,messages)}")


#sends link to twitch channel
@client.command()
async def link(ctx):
    await ctx.send(f"https://www.twitch.tv/krypticphox")


@client.command()
async def livecheck(ctx):
    if(islive()):
        await ctx.send("Channel is live")
    else: 
        await ctx.send("Channel is not live")


#Background task which checks if specified twitch channel is live, if it is check if it has been announced,
#  if it hasn't been announce it and set announce to True, if it has been announced check back in 60 seconds
#   If channel is not live set announce to False and check back in 60 seconds
async def channel_check():
    announce = False
    while True:
        if islive():
            if announce == False:
                channel = client.get_channel(int(NOTIF_CHANNEL))
                await channel.send(f"{NOTIF_ROLE} KrypticPhox is live https://www.twitch.tv/krypticphox ")
                announce = True
        else: announce = False
        await asyncio.sleep(60)

#runs bot

client.run(TOKEN)



