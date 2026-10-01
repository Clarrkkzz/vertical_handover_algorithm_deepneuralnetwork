#!/usr/bin/python

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def create_handoff_network():
    # Initialize network with Strongest Signal First (ssf) auto-association enabled
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference, ac_method='ssf')

    info("*** Adding nodes\n")
    # Both APs share the same SSID for roaming capability
    ap1 = net.addAccessPoint('ap1', ssid='roam-net', mode='g', channel='1', position='10,50,0')
    ap2 = net.addAccessPoint('ap2', ssid='roam-net', mode='g', channel='6', position='90,50,0')
    
    # Station starts right next to ap1
    sta1 = net.addStation('sta1', position='12,50,0')
    c0 = net.addController('c0')

    info("*** Configuring WiFi nodes\n")
    net.configureWifiNodes()

    info("*** Plotting Graph\n")
    net.plotGraph(max_x=100, max_y=100)

    info("*** Adding links\n")
    net.addLink(ap1, ap2)

    info("*** Configuring Mobility\n")
    # Move sta1 slowly from near ap1 (X=12) all the way past ap2 (X=88) over 40 seconds
    net.startMobility(time=0, ac_method='ssf')
    net.mobility(sta1, 'start', time=1, position='12,50,0')
    net.mobility(sta1, 'stop', time=40, position='88,50,0')
    net.stopMobility(time=41)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])

    info("*** Starting CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_handoff_network()