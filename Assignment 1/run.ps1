start powershell "pip install numpy"
pause

start powershell "python UAV.py uav1"
start powershell "python UAV.py uav2"
start powershell "python UAV.py uav3"
start powershell "python UAV.py uav4"
start powershell "python UAV.py uav5"
start powershell "python UAV.py uav6"
Start-Sleep -s 1
start powershell "python HQ.py"