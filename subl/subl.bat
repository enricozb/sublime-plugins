IF %1 EQU "push" SET src = "C:/Users/michael.opara.1/%2" & SET dst = "H:/WORK/%2"
IF %1 EQU "pull" SET src = "H:/WORK/%2" & SET dst = "C:/Users/michael.opara.1/%2"
RD /S /Q %dst%
ROBOCOPY %src% %dst% /E 
PAUSE
