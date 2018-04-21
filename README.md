# Discord Bot for Automated UE4-PS4 Builds

This bot was created with the intent of being run on a separate machine that will on a scheduled basis, 
get the latest from the perforce directory where the project is based, attempt to package the project for PS4 (using RunUAT.bat),
and ping all developers in the chat when a build fails.

Bot features:
* Provides hourly build between working hours (see minTime & maxTime).
* Manual build command for developers to start a build when needed.
* Output the error messages from the RunUAT.bat output into discord channel and most recent 3 commits in project directory.
* Return the state of build attempt and ping the appropriate users (the requester or @everyone if scheduled fails)

### Prerequisites

The following is required on the machine on which the bot is to be run on:

```
Unreal Engine 4
Windows Operating System (to run .bat files)
Python 3.5 or greater.
Perforce
```
Note: This stage assumes the bot was already added to the discord server on which this bot is intended to be run.

### Installing & Setup

The correct system environment variables and perforce variables are needed for the scripts to work correctly.

```
 - Add p4v.exe location to 'PATH' environment variable.
 - Open CMD and use 'p4 set' <...> to set the perforce variables (P4CLIENT/P4PORT/P4USER etc.)
 - In CMD, run 'pip install discord.py' to download the python wrapper for discord.
 - Edit the .bat files in 'BatchFiles/' to use the directories for your machine as needed (e.g. location of RunUAT.bat)
```

## Running & Using the bot
Run the python script in 'DiscordBot/' using your installation of python.

Command List:
* '!help'			- Show command list.
* '!buildrequest'	- Manual build command (ignored if one is in progress)

## Acknowledgments

* [Discord.py] (https://github.com/Rapptz/discord.py) is the work of Rapptz. An API wrapper for discord.