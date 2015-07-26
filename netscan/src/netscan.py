'''
Created on Jul 24, 2015

@author: max
'''

from wifi.scan import Cell
from apscheduler.schedulers.blocking import BlockingScheduler
import pynotify
import logging


'''
For APScheduler stacktrace
'''
logging.basicConfig()

'''
A list of the scanned networks from last time.
**ONLY Network classes go into this
'''
prevNetworks = []

'''
A list of the addresses of happy networks that the netscan daemon
has aleady notified the user of
***NOTE: Only keep network MAC Addresses on this list if they stay
a part of the lasting networks. If not, remove them as we might encounter
them again later on
'''
notedNetworks = []

'''
We store each network as a class with only the values we require
***From now on use MAC Address like you would a UUID in minecraft.
The point: DON'T USE THE NAMES OF NETWORKS. (Ex: two xfinitywifi networks in one area)
***Different MAC Address for a wifi extender? That would suck quite frankly
'''
class Network():
    def __init__(self,ssid,address,signal,encrypted):
        self.ssid = ssid
        self.address = address
        self.signal = signal
        self.count = 0
        self.encrypted = encrypted

def getNetworkFromSSID(networks,ssid):
    for network in networks:
        if (network.ssid == ssid):
            return network
    return None

def getNetworkFromMAC(networks,address):
    for network in networks:
        if (network.address == address):
            return network
    return None

def removeNetwork(networks,ssid):
    deletedNetwork = None
    for network in networks:
        if (network.ssid == ssid):
            deletedNetwork = network
            break
    networks.remove(deletedNetwork)
            
'''
The method called by the blocking scheduler
'''
def tick():
    '''
    ***REMOVE IF WE CAN TELL IF WE ARE CONNECTED
    If there is only 1 wifi network, it means
    that we are already connected or that there
    is only 1 wifi network. Do nothing since the
    user can try and connect to that network
    on there own.
    '''
    '''
    A list of the addresses of networks that are repetitive with each scan.
    Make the noted and previous network lists global
    '''
    global prevNetworks
    global notedNetworks
    
    lastingNetworks = []

    '''
    Parse the data from the already parsed data of
    Cell.all("wlan0") and turn it into a list of
    the wifi networks each represented by the 
    Network class. When parsing, if a network has
    the name of another in the list, keep/add
    whichever network has the strongest signal.
    If each have the same signal, choose the
    current network being iterated over.
    Ex: Two seperate xfinitywifi networks.
    '''
    liveNetworks = []
    for network in Cell.all("wlan0"):
        ssid = network.ssid
        address = network.address
        signal = round(int((network.quality.split("/")[0]))/.7)
        encrypted = network.encrypted
        parsedNetwork = Network(ssid,address,signal,encrypted)
        if (getNetworkFromSSID(liveNetworks, ssid) is not None):
            otherNetwork = getNetworkFromSSID(liveNetworks, ssid)
            if (otherNetwork.signal <= signal):
                removeNetwork(liveNetworks, ssid)
                liveNetworks.append(parsedNetwork)
        else:
            liveNetworks.append(parsedNetwork)
    
    '''
    With our fresh set of live parsed networks,
    we now need to compare them with our older
    previous set of networks so that we can
    update the vital list of lasting networks.
    We also need to average out the signal from
    the previous signal and current signal for
    more accuracy and increase the amount of times
    this network has been scanned in a row if it appears
    in the list of old networks. We also need to add
    its MAC Address if it's not already in the lasting
    list of networks.
    '''
            
    for network in liveNetworks:
        if (not(getNetworkFromMAC(prevNetworks,network.address) == None)):
            oldNetwork = getNetworkFromMAC(prevNetworks,network.address)
            network.count = (oldNetwork.count + 1)
            network.signal = round((network.signal + oldNetwork.signal) / 2)
            if (notedNetworks.count(network.address) == 0 and 
                lastingNetworks.count(network.address) == 0):
                lastingNetworks.append(network.address)
                
    
    '''
     Run through our list of lasting networks and check
     if each network has had an average signal of 50% or
     above and has been scanned 3 times in a row. If so,
     display the notification that the network is available
     and remove it from the list of lasting network MACs.
     Add it to the list of noted networks so it doesn't
     get thrown back in the mix.
    '''
                
                
    '''
    Remove noted network MAC addresses if they no longer are lasting
    '''
    
    removedMACS = []
    for address in lastingNetworks:
        network = getNetworkFromMAC(liveNetworks, address)
        if (network.signal >= 50 and network.count >= 3):
            removedMACS.append(address)
            if (notedNetworks.count(address) == 0):
                notedNetworks.append(address)
                ssid = network.ssid
                encrypted = None
                if (network.encrypted is True):
                    encrypted = "Yes"
                else:
                    encrypted = "No"
                if ("x00" in str(ssid)):
                    ssid = "Unknown"
            pynotify.init("netscan - " + network.ssid)
            notification = pynotify.Notification("Network Detected",
            "SSID: " + ssid + "\n" + "Signal Strength: " + str(network.signal).replace(".0", "") + "%\n" + "Encrypted: " + encrypted,
            "/home/max/tools/icons/wifi.png")
            notification.show()
            
    for address in removedMACS:
        lastingNetworks.remove(address)
        
    prevNetworks = liveNetworks
'''
Initiate a new instance of a scheduler and add the calling
of the tick() function task every 8 seconds.
Start the task and if there's an error
clean it up if it involves the program
exiting or a keyboard error happening
or 
'''
task = BlockingScheduler()
task.add_job(tick, 'interval', seconds=8)
try:
    task.start()
except (KeyboardInterrupt, SystemExit):
    pass
    
            
