ECHO OFF

IF "%1" == "push" (
    SET src="C:/Users/michael.opara.1/%2"
    SET dst="H:/WORK/%2"
)

IF "%1" == "pull" (
    SET src="H:/WORK/%2"
    SET dst="C:/Users/michael.opara.1/%2"
)

IF EXIST "%dst%" (
    RD /S /Q %dst%
)

IF EXIST "%src%" (
    ROBOCOPY %src% %dst% /E 
)
