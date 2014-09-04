@ECHO OFF

IF %1 EQU push (
    SET src=C:/Users/michael.opara.1
    SET dst=H:/WORK
)

IF %1 EQU pull (
    SET src=H:/WORK
    SET dst=C:/Users/michael.opara.1
)

FOR /F %%G IN ('DIR /B %2') DO (
    SET src=%src%/%%G
    SET dst=%dst%/%%G

    IF EXIST %src (
        RD /S /Q %dst%
    )
    
    ROBOCOPY %src% %dst% /E 
)
