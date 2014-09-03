@ECHO OFF

IF "%1"=="push" (
    SET src="C:/Users/michael.opara.1"
    SET dst="H:/WORK"
)

IF "%1"=="pull" (
    SET src="H:/WORK"
    SET dst="C:/Users/michael.opara.1"
)

FOR "%G" IN ("%2") DO (
    RD /S /Q "%dst%/%G"
    ROBOCOPY "%src%/%G" "%dst%/%G" /E 
)
