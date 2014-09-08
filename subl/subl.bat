@ECHO OFF

IF %1 EQU push (
    SET srcdir=C:\Users\michael.opara.1
    SET dstdir=H:\WORK
)

IF %1 EQU pull (
    SET srcdir=H:\WORK
    SET dstdir=C:\Users\michael.opara.1
)

FOR /F "usebackq delims=|" %%G IN (`FORFILES /p "%srcdir%" /m %2`) DO (
    SET src=%srcdir%/%%G
    SET dst=%dstdir%/%%G

    IF EXIST %dst% (
        RD /S /Q %dst%
    )
    
    ROBOCOPY %src% %dst% /E
)
