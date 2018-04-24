import re
import os

dir = os.path.dirname(__file__)
UATLogFile = os.path.join(dir, '..', 'BatchFiles', 'BlueprintErrors.log')
warningLogString = ""
errorLogString = ""


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
                
    return errorLogString
   
warningStr = FindWarningsInBuildOutput()
errorStr = FindErrorsInBuildOutput()

with open("WarningLog.txt", "w") as text_file:
    text_file.write(warningStr)
with open("ErrorLog.txt", "w") as text_file:
    text_file.write(errorStr)



#create chunks
#chunks, chunk_size = len(errorStr), 1900
#list = [ errorStr[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]

#for x in list:
#   print(x)


#print(FindErrorsInBuildOutput())