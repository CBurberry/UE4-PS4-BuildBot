@echo off
@echo argument 1 is %1%

REM Change working directory to the batch file directory.
CD %~dp0

REM Location of the default package
set ProjectDir=V:/Perforce-V/GamerCamps/Pro2017/Mod4/Work/WhiteBoxProject
set ContentID=IV0000-TEST00000_00-TESTTESTTESTTEST
set Package=%ProjectDir%/PlatformBuilds/PS4/%ContentID%/WhiteBoxProject-%ContentID%.pkg

REM Delete old logfile if it exists
del Package.log

REM Turn on the target dev kits - output to console from file when command finished.
call PS4ToolShortcut.lnk -on %1% > Package.log 2>&1
type Package.log

REM Shortcut to PS4 SDK Utility - output to console from file when command finished.
call PS4ToolShortcut.lnk -pkg-install %Package% %1% > Package.log 2>&1
type Package.log

exit /B 0