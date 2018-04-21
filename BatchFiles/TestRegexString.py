import re
import os

dir = os.path.dirname(__file__)
UATLogFile = os.path.join(dir, '..', 'BatchFiles', 'UE4output.log')
errorLogString = ""

#Function that parses the log file from UAT output line by line to match errors
# if any errors are found, they are returned as a string for print output.
def FindErrorsInBuildOutput():
    global errorLogString
    errorLogString = "\n\n**Error Output:**\n\n```"
    firstErrorEncountered = None
    endOfErrorEncountered = None
    with open(UATLogFile) as file:
        for line in file:    
            if ( endOfErrorEncountered == None ):
                # Check for the starting error
                if ( firstErrorEncountered == None ):
                    firstErrorEncountered = re.search('error:', line)
                
                # We check if the ending line to error output was found
                endOfErrorEncountered = (re.search(' error generated.', line) or re.search(' errors generated.', line))
                
                # If the starting error was found add the line to the string.
                if not ( firstErrorEncountered == None ):
                    errorLogString = errorLogString + line
    errorLogString = errorLogString + "\n```"
    return errorLogString
    
errorStr =  FindErrorsInBuildOutput()

#create chunks
chunks, chunk_size = len(errorStr), 1900
list = [ errorStr[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]

for x in list:
    print(x)


#print(FindErrorsInBuildOutput())