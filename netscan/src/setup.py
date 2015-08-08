'''
Created on Jul 25, 2015
@author: max
***RUN AS ROOT
1. Install the two required python libraries, wifi and python-notify.
3. Create a new instance of netscan.desktop and input the details (name, command, etc.)
4. Test out the new netscan-notify library by alerting the user that the setup process has finished.
'''
from subprocess import call
from os import path

__folder__ = ""
i = 0
split = str(__file__).split("/")
while i < (len(split) - 1):
    __folder__ = __folder__ + split[i] +  "/"
    i+=1
    
call(['pip', 'install','wifi'])
call(['apt-get', 'install','python-notify'])
data = "[Desktop Entry]\nType=Application\nExec=python " + __folder__ + "netscan.netscan\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\nName[en_US]=netscan\nName=netscan\nComment[en_US]=Launches the netscan python script\nComment=Launches the netscan python script\n"
with open(path.join(path.expanduser("~") + "/.config/autostart/","netscan.desktop"), "w") as f:
    f.write(data)
    
import pynotify

pynotify.init("netscan setup")
n = pynotify.Notification("Netscan Installation Finished","You have successfully installed netscan.")
n.show()
