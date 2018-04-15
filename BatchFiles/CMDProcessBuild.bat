@echo off
setlocal EnableExtensions EnableDelayedExpansion

set ProjectDir=V:\Perforce-V\GamerCamps\Pro2017\Mod4\Work\WhiteBoxProject
set LogDir=%~dp0

::call p4 sync --parallel=0 //depot/GamerCamps/Pro2017/Mod4/Work/WhiteBoxProject/...#head - reenable this
REM Maybe log the latest changelog BEFORE doing the build? A new commit may have happened during build.
call %~dp0\TestBAT.bat

if not !errorlevel! == 0 ( 
	REM CD /D %ProjectDir%
	REM ::Log the latest changelist detail.
	REM call p4 changelists -m 1 -l -t "//depot/GamerCamps/Pro2017/Mod4/Work/WhiteBoxProject/..." > %LogDir%/output.log 
	echo "Perforce Calls / Unsuccessful" 
	exit /B 1
) else ( 
	echo "Successful Build!" 
	exit /B 0
)