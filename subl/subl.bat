IF %1 EQU "push" set src = "C:/Users/michael.opara.1/%2" & set dst = "H:/WORK/%2"
IF %1 EQU "pull" set src = "H:/WORK/%2" & set dst = "C:/Users/michael.opara.1/%2"
RD /S /Q %dst%
ROBOCOPY %src% %dst% /E 
PAUSE
