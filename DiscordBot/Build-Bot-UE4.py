import discord
import asyncio
import subprocess
import threading
import datetime
import os
from queue import *

client = discord.Client()
dir = os.path.dirname(__file__)
buildScript = os.path.join(dir, '..','BatchFiles','CMDProcessBuild.bat')
logFile = os.path.join(dir, '..','BatchFiles','output.log')

#Text channel in which the bot posts to
channelID = '430738765372325900'

#Global variable boolean for tracking if a build is in progress.
isBuildInProgress = False

#Queue for logging strings (workaround for threading string passing)
messageQueue = Queue(maxsize=1)

#Number of currently active threads at startup
startupThreadCount = threading.active_count()

#The minimum and maximum hours between which builds will be auto-scheduled (10:00 - 16:00)
minTime = datetime.time(hour=10)
maxTime = datetime.time(hour=16)

# task runs every hour
buildInterval = 3600

#Parallel script runner (not running in parallel causes discord to disconnect the bot)
class ParallelThread(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)
       
    #Function that runs the script locally and outputs the result to the messageQueue
    def RunBuildScript(self):
        isBuildInProgress = True
        p = subprocess.Popen(buildScript, shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        self.stdout, self.stderr = p.communicate() 
        outString = ""
        print('subprocess started')
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
        messageQueue.put(outString)
    
    def run(self):
        self.RunBuildScript()
        print('RunBuildScript Finished!')

#Function that checks if the current time is in the schedule range.
def IsCurrentTimeInRange():
    currentTime = datetime.datetime.now().time()
    returnValue = False
    if minTime <= currentTime and currentTime <= maxTime:
        returnValue = True
    return returnValue

#Function that builds the application in the given scheduled hours
# Starts up a separate thread to run the script
async def Scheduled_Build():
    await client.wait_until_ready()
    channel = discord.Object(id=channelID)
    
    while not client.is_closed:
        #We don't want to run a scheduled build outside of min/max hours.
        if IsCurrentTimeInRange():
            if not isBuildInProgress:
                buildScriptThread = ParallelThread()
                buildScriptThread.start()
                while( buildScriptThread.is_alive() ):
                    print('sleeping for 10s')
                    await asyncio.sleep(10)
                print('thread exited finished!')
                msg = messageQueue.get_nowait()
                if len(msg) > 100:
                    msg = "@everyone " + msg
                await client.send_message(channel, msg)
            else:
                await client.send_message(channel, 'Error: A build is already in progress, build request ignored.')
        #Sleep for scheduled interval time and repeat loop after period elapses.
        await asyncio.sleep(buildInterval)

#Function for manually building rather than scheduling
# does a check if a build is currently running before attempting
# functionally equivalent to Scheduled_Build() pings the caller instead of everyone.
async def Command_Build(message):
    channel = discord.Object(id=channelID)
    if not client.is_closed:
        if not isBuildInProgress:
            buildScriptThread = ParallelThread()
            buildScriptThread.start()
            while( buildScriptThread.is_alive() ):
                print('sleeping for 10s')
                await asyncio.sleep(10)
            msg = messageQueue.get_nowait()
            msg = "{0.author.mention} ".format(message) + msg
        else:
            msg = 'Error: A build is already in progress, build request ignored. ActiveThreads: ' + str(threading.active_count()) 
            msg = msg + ' Default: ' + str(startupThreadCount)
    else:
        msg = "Error: Command could not be executed."
    return msg


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    # run the build command manually.
    if message.content.startswith('!buildrequest'):
        msg = 'Understood {0.author.mention}, executing build....'.format(message)
        await client.send_message(message.channel, msg)
        await client.wait_until_ready()
        msg = await Command_Build( message )
        await client.send_message(message.channel, msg)
    
    # knock knock who's there    
    elif message.content.startswith('!bot'):
        await client.send_message(message.channel, 'You Rang {0.author.mention}?'.format(message))
    
    # list command options
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

#Schedule the task on a event loop and provide the bot API token.
client.loop.create_task(Scheduled_Build())
client.run('NDMwNzM3MTIyNzQ4NjYxNzYx.DaUn5w.iX7Wk13LUOM3VcOD3KjzQv-VmqY')