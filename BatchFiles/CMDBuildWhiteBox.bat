set UATDir=V:\UE4Binary_4.18.3_PS4\Engine\Windows\Engine\Build\BatchFiles
set ProjectDir=V:\Perforce-V\GamerCamps\Pro2017\Mod4\Work\WhiteBoxProject
set ProjectFilename=WhiteBoxProject.uproject
set OutputDirectory=%ProjectDir%\PlatformBuilds
CD /D %UATDir%

REM Below are the commands for platform building - edit as needed

:: Command for building / compiling / cooking for PS4 platform (incl. packaging).
RunUAT BuildCookRun -project=%ProjectDir%\%ProjectFilename% -noP4 -platform=PS4 -clientconfig=Development -serverconfig=Development -cook -allmaps -build -stage -pak -package -archive -archivedirectory=%OutputDirectory%

:: Command for building / compiling / cooking for the Win64 platform (no packaging).
REM RunUAT BuildCookRun -project=%ProjectDir%\%ProjectFilename% -noP4 -platform=Win64 -clientconfig=Development -serverconfig=Development -cook -allmaps -build -stage -pak -archive -archivedirectory=%OutputDirectory%