:: start server in another terminal
start cmd /k python D:\data\code\python\project_mount_christ\src\server\server.py

:: Sleep for 1 seconds
ping -n 1 127.0.0.1 >nul
echo 123


:: start client 3 in another terminal
start cmd /k python D:\data\code\python\project_mount_christ\src\client\client.py t3

ping -n 1 127.0.0.1 >nul

:: start client 2 in another terminal
start cmd /k python D:\data\code\python\project_mount_christ\src\client\client.py t2

ping -n 1 127.0.0.1 >nul

:: start client 1 in another terminal
start cmd /k python D:\data\code\python\project_mount_christ\src\client\client.py t1


