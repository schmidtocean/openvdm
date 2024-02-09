import json
from xmlrpc.client import ServerProxy

user = "mt"
passwd = "Dragon2017"
server = "10.23.9.25"

postFKtProcess = "sealog-FKt-post-cruise-data-export"
postSubProcess = "sealog-Sub-post-cruise-data-export"

server = ServerProxy(f'http://{user}:{passwd}@{server}:9001/RPC2')

procInfo = server.supervisor.getProcessInfo(postFKtProcess)
if procInfo['statename'] != "RUNNING":
	server.supervisor.startProcess(postFKtProcess)
else:
    print(f'{postFKtProcess} process is already running')

procInfo = server.supervisor.getProcessInfo(postSubProcess)
if procInfo['statename'] != "RUNNING":
	server.supervisor.startProcess(postSubProcess)
else:
    print(f'{postSubProcess} process is already running')

