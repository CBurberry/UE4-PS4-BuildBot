@echo off
setlocal EnableExtensions EnableDelayedExpansion

set ProjectDir=V:\Perforce-V\GamerCamps\Pro2017\Mod4\Work\WhiteBoxProject
set LogDir=%~dp0

REM Get the latest from perforce before attempting the build.
call p4 sync --parallel=0 //depot/GamerCamps/Pro2017/Mod4/Work/WhiteBoxProject/...#head
call %~dp0\CMDBuildWhiteBox.bat > %LogDir%/UE4output.log 2>&1 
REM call %~dp0\TestBAT.bat

if not !errorlevel! == 0 ( 
	CD /D %ProjectDir%
	REM Log the latest changelist detail.
	call p4 changelists -m 3 -l -t "//depot/GamerCamps/Pro2017/Mod4/Work/WhiteBoxProject/..." > %LogDir%/perforce.log 
	echo "There was an error!" 
	exit /B 1
) else ( 
	echo "Successful Build!" 
	exit /B 0
)