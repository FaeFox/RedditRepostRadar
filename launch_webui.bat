@echo off
setlocal EnableDelayedExpansion
:begin
echo Starting web_ui.py...
python web_ui.py

rem Check if Python script exited with an error
if not %errorlevel%==0 (
    echo Error detected. Rerunning for error logging...
    python web_ui.py > temp_output.txt 2>&1

    rem Check for ModuleNotFoundError
    find "ModuleNotFoundError" temp_output.txt > nul
    if %errorlevel%==0 (
        echo One or more required Python modules were not found.
        set /p userChoice="Would you like to attempt to install them now? (Y/N) "
        if /i "!userChoice!"=="Y" (
            echo Installing required modules from requirements.txt...
            pip install -r requirements.txt
            echo Modules installed. Restarting...
            goto begin
        ) else if /i "!userChoice!"=="N" (
            echo Required modules not installed. The program will now exit.
            goto end
        ) else (
            echo Invalid choice. Please answer with Y or N.
            goto begin
        )
    )

    rem Check for any other Python error
    find "Traceback (most recent call last):" temp_output.txt > nul
    if %errorlevel%==0 (
        echo Error: A Python error occurred.
        type temp_output.txt
    )

    goto end
)

:end
if exist temp_output.txt del temp_output.txt
pause
