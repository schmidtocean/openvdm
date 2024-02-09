import json
from xmlrpc.client import ServerProxy

user = "mt"
passwd = "Dragon2017"
server = "10.23.9.25"

postSubProcess = "sealog-Sub-post-dive-data-export"

server = ServerProxy(f'http://{user}:{passwd}@{server}:9001/RPC2')

procInfo = server.supervisor.getProcessInfo(postSubProcess)
if procInfo['statename'] != "RUNNING":
	server.supervisor.startProcess(postSubProcess)
else:
    print(f'{postSubProcess} process is already running')

