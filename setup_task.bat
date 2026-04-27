@echo off
schtasks /create /tn "Trump Monitor" /tr "C:\Users\User\AppData\Local\Programs\Python\Python311\python.exe C:\Users\User\Desktop\trump_monitor_project\trump_monitor.py" /sc MINUTE /mo 30 /f
echo.
echo Scheduled task created successfully!
pause
