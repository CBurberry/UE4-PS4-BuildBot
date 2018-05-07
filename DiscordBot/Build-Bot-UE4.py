import discord
import asyncio
import subprocess
import threading
import datetime
import os
import re
from queue import *

client = discord.Client()
dir = os.path.dirname(__file__)
buildScript = os.path.join(dir, '..', 'BatchFiles', 'CMDProcessBuild.bat')
getLatestScript = os.path.join(dir, '..', 'BatchFiles', 'CMDGetForcedLatest.bat')
installPackageScript = os.path.join(dir, '..', 'BatchFiles', 'CMDInstallPackage.bat')
perforceLogFile = os.path.join(dir, '..', 'BatchFiles', 'perforce.log')
packageLogFile = os.path.join(dir, '..', 'BatchFiles', 'Package.log')
UATLogFile = os.path.join(dir, '..', 'BatchFiles', 'UE4output.log')
wLogFilename = os.path.join(dir, '..', 'BatchFiles', 'WarningLog.log')
eLogFilename = os.path.join(dir, '..', 'BatchFiles', 'ErrorLog.log')
warningLogString = ""
errorLogString = ""
batchScriptRunValue = 0

#Text channel in which the bot posts to
channelID = '430738765372325900'

#Global variable boolean for tracking if a build is in progress.
isOperationInProgress = False

#Queue for logging strings (workaround for threading string passing)
messageQueue = Queue(maxsize=1)

#The minimum and maximum hours between which builds will be auto-scheduled (10:00 - 16:00)
minTime = datetime.time(hour=10)
maxTime = datetime.time(hour=16)

# task runs every hour
buildInterval = 3600

#Parallel script runner (not running in parallel causes discord to disconnect the bot)
class ParallelThread(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        self.args = args
    
    def RunGetLatestScript(self):
        global isOperationInProgress
        isOperationInProgress = True
        p = subprocess.Popen(getLatestScript, shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        self.stdout, self.stderr = p.communicate() 
        print('subprocess started')
        isOperationInProgress = False
        messageQueue.put("Revision forced to #head")
    
    #Function that runs the script locally and outputs the result to the messageQueue
    def RunBuildScript(self):
        global isOperationInProgress
        isOperationInProgress = True
        p = subprocess.Popen(buildScript, shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        self.stdout, self.stderr = p.communicate() 
        outString = ""
        print('subprocess started')
        if p.returncode != 0:
            data = "**PS4 Build Failed!** \n\n"
            data += "====================================================================================================\n\n"
            data += "**Recent commits in the project directory**:\n\n"
            with open(perforceLogFile, 'r') as myfile:
                data += myfile.read()
            data += "===================================================================================================="
            outString = data
            WriteWarningsErrorsToFiles()
            if not ( len(errorLogString) == 0 ):
                outString += "\nView logfiles for detailed error and warning outputs (command: !getlogs)\n"
        else:
            outString = "Build Successful"
        isOperationInProgress = False
        messageQueue.put(outString)
    
    def RunPackageInstall(self):
        global isOperationInProgress
        isOperationInProgress = True
        p = subprocess.Popen([installPackageScript, self.args[0]], shell=False, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        self.stdout, self.stderr = p.communicate() 
        outString = ""
        with open(packageLogFile) as file:
            first_line = file.readline()
            errorSearchValue = re.search('ERROR', first_line)
            invalidSearchValue = re.search('Invalid DevKit:', first_line)
            if ( errorSearchValue != None or invalidSearchValue != None ):
                outString = first_line
            else:
                outString = "Package installed successfully!"
        isOperationInProgress = False
        messageQueue.put(outString)
    
    def run(self):
        print('Args are: {}'.format(self.args))
    
        global batchScriptRunValue
        if ( batchScriptRunValue == 1 ):
            self.RunGetLatestScript()
        if ( batchScriptRunValue == 2 ):
            self.RunBuildScript()
        if ( batchScriptRunValue == 3 ):
            self.RunPackageInstall()
        
        print('Script Finished!')
        batchScriptRunValue = 0
        

        
#Function that checks if the current time is in the schedule range.
def IsCurrentTimeInRange():
    currentTime = datetime.datetime.now().time()
    returnValue = False
    if minTime <= currentTime and currentTime <= maxTime:
        returnValue = True
    return returnValue

    
#Function that parses the log file from UAT output line by line to match warnings
def FindWarningsInBuildOutput():
    global warningLogString
    warningLogString = "\n\n**Warning Output:**\n" + "\nNote: Only the first 50 errors will be shown!\n\n"
    with open(UATLogFile) as file:
        for line in file:  
        
            #All warning types
            warningSearchValue = re.search(' Warning: ', line)
            if ( warningSearchValue != None ):
                warningLogString = warningLogString + line   
                
    warningLogString = warningLogString + "\n"
    return warningLogString

    
#Function that parses the log file from UAT output line by line to match errors
# if any errors are found, they are returned as a string for print output.
def FindErrorsInBuildOutput():
    global errorLogString
    errorLogString = "\n\n**Error Output:**\n\n"
    firstErrorEncountered = None
    endOfErrorEncountered = None
    with open(UATLogFile) as file:
        for line in file:   
            
            #Compiler errors
            if ( endOfErrorEncountered == None ):
                # Check for the starting error
                if ( firstErrorEncountered == None ):
                    firstErrorEncountered = re.search('error:', line)
                
                # We check if the ending line to error output was found
                endOfErrorEncountered = (re.search(' error generated.', line) or re.search(' errors generated.', line))
                
                # If the starting error was found add the line to the string.
                if not ( firstErrorEncountered == None ):
                    errorLogString = errorLogString + line     
                    
    errorLogString = errorLogString + "\n\n"
    with open(UATLogFile) as file:
        for line in file:

            #All other error types
            errorSearchValue = re.search(' Error: ', line)
            if ( errorSearchValue != None ):
                errorLogString = errorLogString + line
            
            #Add the closing failure statement if it exists
            failSearchValue = re.search(' Failure - ', line)
            if ( failSearchValue != None ) :
                errorLogString = errorLogString + '\n\n' + line
  
    #Truncate the error string if there's nothing in it.
    if len(errorLogString) < 50:
        errorLogString = ""
    
    #Formatting fix (replace tilde character with hyphon - discord does line crossout if 2 on either side of a line)
    formattedString = re.sub(r'~', '-', errorLogString)
    return formattedString

    
#Function that outputs the warning and error strings to log files.
def WriteWarningsErrorsToFiles():
    warningStr = FindWarningsInBuildOutput()
    errorStr = FindErrorsInBuildOutput()

    with open(wLogFilename, "w") as text_file:
        text_file.write(warningStr)
    with open(eLogFilename, "w") as text_file:
        text_file.write(errorStr)
        
    
#Function takes a string and sends it out in chunks that fall below the 2k character limit
# Can be improved further with formatting work (aka don't cut a message halfway in chunk separation)
async def SendMessageInChunks(channel, inputString):
    #Convert string to list
    chunks, chunk_size = len(inputString), 1900
    list = [ inputString[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]
    
    #loop while characters remain etc.
    for stringPartition in list:
        await client.send_message(channel, stringPartition)

        
#Function that builds the application in the given scheduled hours
# Starts up a separate thread to run the script
async def Scheduled_Build():
    await client.wait_until_ready()
    channel = discord.Object(id=channelID)
    
    while not client.is_closed:
        #We don't want to run a scheduled build outside of min/max hours.
        if IsCurrentTimeInRange():
            if not isOperationInProgress:
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
                if ( batchScriptRunValue == 1 ):
                    msg = "Error: Currently getting latest from perforce, please try again later."
                if ( batchScriptRunValue == 2 ):
                    msg = 'Error: A build is in progress, please retry later.'
                if ( batchScriptRunValue == 3 ):
                    msg = 'Error: A package is currently being installed on a DevKit(s).'
        #Sleep for scheduled interval time and repeat loop after period elapses.
        await asyncio.sleep(buildInterval)

        
#Function for manually building rather than scheduling
# does a check if a build is currently running before attempting
# functionally equivalent to Scheduled_Build() pings the caller instead of everyone.
async def Command_Script(message, scriptValue, args=[]):
    global batchScriptRunValue
    channel = discord.Object(id=channelID)
    if not client.is_closed:
        if not isOperationInProgress:
            batchScriptRunValue = scriptValue
            buildScriptThread = None
            if (scriptValue == 3):
                buildScriptThread = ParallelThread(args)
            else:
                buildScriptThread = ParallelThread()
            buildScriptThread.start()
            while( buildScriptThread.is_alive() ):
                print('sleeping for 10s')
                await asyncio.sleep(10)
            msg = messageQueue.get_nowait()
            msg = "{0.author.mention} ".format(message) + msg
        else:
            if ( batchScriptRunValue == 1 ):
                msg = "Error: Currently getting latest from perforce, please try again later."
            if ( batchScriptRunValue == 2 ):
                msg = 'Error: A build is in progress, please retry later.'
            if ( batchScriptRunValue == 3 ):
                msg = 'Error: A package is currently being installed on a DevKit(s).'
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
        msg = await Command_Script( message, 2 )
        await client.send_message(message.channel, msg)
    
    # run the get latest script
    elif message.content.startswith('!getlatest'):
        msg = 'Understood {0.author.mention}, getting latest from perforce....'.format(message)
        await client.send_message(message.channel, msg)
        await client.wait_until_ready()
        msg = await Command_Script( message, 1 )
        await client.send_message(message.channel, msg)
    
    # Upload the log files from the build machine
    elif message.content.startswith('!getlogs'):
        msg = 'Understood {0.author.mention}, retrieving log files....'.format(message)
        await client.send_message(message.channel, msg)
        await client.wait_until_ready()
        if ( batchScriptRunValue != 2 ):
            await client.send_file(message.channel, wLogFilename)
            await client.send_file(message.channel, eLogFilename)
            await client.send_file(message.channel, UATLogFile)
        else:
            await client.send_message(message.channel, "Error: Build in progress. ")
    
    # Deploy the package file
    elif message.content.startswith('!sendpackage'):
        msg = 'Understood {0.author.mention}, attempting to send package...'.format(message)
        await client.send_message(message.channel, msg)
        await client.wait_until_ready()
        parameter = message.content.split()[1]
        msg = await Command_Script( message, 3, parameter )
        await client.send_message(message.channel, msg)
    
    # knock knock who's there    
    elif message.content.startswith('!bot'):
        await client.send_message(message.channel, 'You Rang {0.author.mention}?'.format(message))
    
    # list command options
    elif message.content.startswith('!help'):
        helpmsg = """```COMMAND LIST:
                    \n\t!getlatest              - force get latest from perforce for WhiteBoxProject
                    \n\t!getlogs                - get the log files from the build machine
                    \n\t!buildrequest           - request a PS4 build (packaging)
                    \n\t!sendpackage <arg>      - install the game package on the specified IP e.g. '!sendpackage 10.122.6.68' OR for all devkits '!sendpackage *'```"""
        await client.send_message(message.channel, helpmsg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

#Schedule the task on a event loop and provide the bot API token. - Scheduling disabled as not needed.
#client.loop.create_task(Scheduled_Build())
client.run('NDMwNzM3MTIyNzQ4NjYxNzYx.DaUn5w.iX7Wk13LUOM3VcOD3KjzQv-VmqY')