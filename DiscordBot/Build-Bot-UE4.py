import discord
import asyncio
import subprocess
import datetime
import os

client = discord.Client()
dir = os.path.dirname(__file__)
buildScript = os.path.join(dir, '..','BatchFiles','CMDProcessBuild.bat')
logFile = os.path.join(dir, '..','BatchFiles','output.log')
channelID = '430738765372325900'
isBuildInProgress = False

#The minimum and maximum hours between which builds will be auto-scheduled (10:00 - 16:00)
minTime = datetime.time(hour=10)
maxTime = datetime.time(hour=16)

# task runs every hour
buildInterval = 3600

def IsCurrentTimeInRange():
    currentTime = datetime.datetime.now().time()
    returnValue = False
    if minTime <= currentTime and currentTime <= maxTime:
        returnValue = True
    return returnValue

def RunBuildScript():
    isBuildInProgress = True
    p = subprocess.Popen(buildScript, shell=True, stdout = subprocess.PIPE)
    stdout, stderr = p.communicate() 
    outString = ""
    if p.returncode != 0:
        data = "**PS4 Build Failed!** \n\n"
        data += "====================================================================================================\n\n"
        data += "**Most recent commit in the project directory**:\n\n"
        with open(logFile, 'r') as myfile:
            data += '\t' + myfile.read()
        data += "\n===================================================================================================="
        outString = data
    else:
        outString = "Build Successful"
    isBuildInProgress = False
    return outString

async def Scheduled_Build():
    await client.wait_until_ready()
    channel = discord.Object(id=channelID)
    
    while not client.is_closed:
        #We don't want to run a scheduled build outside of min/max hours.
        if not IsCurrentTimeInRange():
            #await client.send_message(channel, 'Outside of hours, build postponed')
        else:
            if not isBuildInProgress:
                msg = RunBuildScript()
                if len(msg) > 100:
                    msg = "@everyone " + msg
                await client.send_message(channel, msg)
            else:
                await client.send_message(channel, 'Error: A build is already in progress, build request ignored.')
        await asyncio.sleep(buildInterval)

def Command_Build(message):
    channel = discord.Object(id=channelID)
    msg = ""
    if not client.is_closed:
        if not isBuildInProgress:
            msg = RunBuildScript()
            msg = "{0.author.mention} ".format(message) + msg
        else:
            msg = 'Error: A build is already in progress, build request ignored.'
    else:
        msg = "Error: Command could not be executed."
    return msg


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!buildrequest'):
        msg = 'Understood {0.author.mention}, executing build....'.format(message)
        await client.send_message(message.channel, msg)
        await client.wait_until_ready()
        msg = Command_Build( message )
        await client.send_message(message.channel, msg)
        
    elif message.content.startswith('!bot'):
        await client.send_message(message.channel, 'You Rang {0.author.mention}?'.format(message))
        
    elif message.content.startswith('!help'):
        helpmsg = """COMMAND LIST:
                    \n\t!buildrequest - request a PS4 build"""
        await client.send_message(message.channel, helpmsg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.loop.create_task(Scheduled_Build())
client.run('NDMwNzM3MTIyNzQ4NjYxNzYx.DaUn5w.iX7Wk13LUOM3VcOD3KjzQv-VmqY')