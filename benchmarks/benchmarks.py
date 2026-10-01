#!/usr/bin/python

import time
import threading
import matplotlib
# Use 'Agg' backend so it can generate and save the plot image cleanly without GUI crashes
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

# Global lists to record telemetry over time
time_log = []
rssi_ap1_log = []
rssi_ap2_log = []

def telemetry_logger(sta, duration=35):
    """Background thread that samples RSSI values every second as the station moves."""
    start_time = time.time()
    info("\n*** [Telemetry Tracker] Logging started...\n")
    
    while time.time() - start_time < duration:
        current_time = round(time.time() - start_time, 1)
        
        try:
            # Query the RSSI from the station interface
            # Mininet-WiFi automatically calculates path loss based on current (x,y) coordinates
            rssi = sta.wintfs[0].rssi
            
            # Log data
            time_log.append(current_time)
            rssi_ap1_log.append(rssi) # (In a multi-AP setup, you can query specific links or overall RSSI)
            
            print(f"[Time: {current_time}s] Station RSSI: {rssi} dBm")
        except Exception as e:
            pass
            
        time.sleep(1)
        
    info("*** [Telemetry Tracker] Logging finished.\n")

def generate_rssi_graph():
    """Generates a visual performance graph of RSSI over time and saves it as a PNG."""
    if not time_log:
        info("*** No telemetry data recorded to plot.\n")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(time_log, rssi_ap1_log, label='RSSI Signal (dBm)', color='blue', linewidth=2, marker='o', markersize=3)
    
    plt.title('Station RSSI Over Time During Movement (Base Station Handoff)', fontsize=12)
    plt.xlabel('Time (Seconds)', fontsize=10)
    plt.ylabel('RSSI (dBm)', fontsize=10)
    plt.axhline(y=-75, color='red', linestyle='--', label='Handover Threshold (-75 dBm)')
    
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    # Save graph directly to workspace folder
    output_path = 'handoff_rssi_performance.png'
    plt.savefig(output_path)
    info(f"\n*** [Graph Generated] Saved performance chart to: {output_path}\n")

def run_simulation():
    # Initialize network with Strongest Signal First (ssf) auto-association
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference, ac_method='ssf')

    info("*** Adding nodes\n")
    ap1 = net.addAccessPoint('ap1', ssid='roam-net', mode='g', channel='1', position='10,50,0')
    ap2 = net.addAccessPoint('ap2', ssid='roam-net', mode='g', channel='6', position='90,50,0')
    
    sta1 = net.addStation('sta1', position='12,50,0')
    c0 = net.addController('c0')

    info("*** Configuring WiFi nodes\n")
    net.configureWifiNodes()

    # Optional: Open live map visualization window if X11/VcXsrv is active
    try:
        net.plotGraph(max_x=100, max_y=100)
    except Exception:
        pass

    info("*** Adding links\n")
    net.addLink(ap1, ap2)

    info("*** Configuring Mobility (Moving sta1 from AP1 toward AP2)\n")
    # Move sta1 from X=12 to X=88 over 30 seconds
    net.startMobility(time=0, ac_method='ssf')
    net.mobility(sta1, 'start', time=1, position='12,50,0')
    net.mobility(sta1, 'stop', time=30, position='88,50,0')
    net.stopMobility(time=31)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])

    # Start the background data logger thread
    logger_thread = threading.Thread(target=telemetry_logger, args=(sta1, 35))
    logger_thread.daemon = True
    logger_thread.start()

    info("*** Starting CLI (Type 'exit' when simulation concludes)\n")
    CLI(net)

    # After exiting the CLI, automatically generate the metrics graph
    info("*** Shutting down network and generating analytics...\n")
    generate_rssi_graph()
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_simulation()