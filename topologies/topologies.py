import sys
import os

# Ensure the root project folder is first in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from movement.verticalhandover import start_vertical_handover

def topology():
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    # Mobile station moving within the defined coordinate bounds
    sta1 = net.addStation(
        'sta1', 
        mac='00:00:00:00:00:01', 
        ip='10.0.0.1/8',
        min_x=10, max_x=90, min_y=10, max_y=90, 
        min_v=2, max_v=5
    )

    # Base stations distributed across a 100x100 grid
    ap_UMTS = net.addAccessPoint('ap1', ssid='UMTS', mode='g', channel='1',  position='20,20,0', range=30)
    ap_GPRS = net.addAccessPoint('ap2', ssid='GPRS', mode='g', channel='6',  position='80,20,0', range=30)
    ap_WLAN = net.addAccessPoint('ap3', ssid='WLAN', mode='g', channel='11', position='20,80,0', range=30)
    ap_4G   = net.addAccessPoint('ap4', ssid='4G',   mode='a', channel='36', position='80,80,0', range=30)
    ap_5G   = net.addAccessPoint('ap5', ssid='5G',   mode='a', channel='40', position='50,50,0', range=30)

    c1 = net.addController('c1')

    info("*** Setting Log-Distance Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring Wi-Fi Nodes\n")
    net.configureWifiNodes()

    info("*** Enabling GUI Visualization Plot\n")
    net.plotGraph(max_x=100, max_y=100)

    info("*** Setting Mobility Model\n")
    net.setMobilityModel(time=0, model='RandomWayPoint', max_x=100, max_y=100, seed=20)

    info("*** Starting Network\n")
    net.build()
    c1.start()
    for ap in [ap_UMTS, ap_GPRS, ap_WLAN, ap_4G, ap_5G]:
        ap.start([c1])

    info("*** Launching Background Handover Engine\n")
    stop_event = start_vertical_handover(sta1, [ap_UMTS, ap_GPRS, ap_WLAN, ap_4G, ap_5G])

    info("*** Entering CLI (Type 'exit' to stop)\n")
    CLI(net)

    stop_event.set()
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()