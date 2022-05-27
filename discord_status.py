from pypresence import Presence 
import time, psutil

start = int(time.time())
app_id = "979521390715752528"
RPC = Presence(app_id)
RPC.connect()

print("[#] Discord RPC connected!")
while True:
    RPC.update(
        large_image = "icon",
        large_text = "PhantomChat",
        details = "Hosting a hub",
        state = "Cpu ussage: " + str(psutil.cpu_percent()) + "%",
        start = start,
        buttons = [{"label": "Check out the project", "url": "https://github.com/MrEnder0/PhantomChat"}]
    )
    time.sleep(15)