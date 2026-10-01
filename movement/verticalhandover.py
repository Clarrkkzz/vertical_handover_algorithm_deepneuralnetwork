import os
import time
import math
import threading
import csv
from mininet.log import info
import joblib

current_dir = os.path.dirname(os.path.abspath(__file__))
algorithms_dir = os.path.join(os.path.dirname(current_dir), 'algorithms')
project_root = os.path.dirname(current_dir)
csv_path = os.path.join(project_root, 'telemetry.csv')

models = {
    net: joblib.load(os.path.join(algorithms_dir, f'{net}_bp_model.pkl'))
    for net in ['UMTS', 'GPRS', 'WLAN', '4G', '5G']
}

NETWORK_PROFILES = {
    'UMTS': {'speed': 3.0, 'max_rate': 1024.0,   'delay': 20.0, 'sinr': 18.0, 'ber': 3.0,  'loss': 0.005},
    'GPRS': {'speed': 3.0, 'max_rate': 115.0,    'delay': 30.0, 'sinr': 16.0, 'ber': 10.0, 'loss': 0.009},
    'WLAN': {'speed': 3.0, 'max_rate': 51200.0,  'delay': 7.0,  'sinr': 22.0, 'ber': 7.0,  'loss': 0.002},
    '4G':   {'speed': 3.0, 'max_rate': 20480.0,  'delay': 15.0, 'sinr': 20.0, 'ber': 0.8,  'loss': 0.001},
    '5G':   {'speed': 3.0, 'max_rate': 102400.0, 'delay': 1.0,  'sinr': 25.0, 'ber': 0.01, 'loss': 0.0001}
}

def get_distance(node1, node2):
    pos1 = node1.position
    pos2 = node2.position
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def collect_network_parameters(station, ap, distance):
    ssid = ap.params['ssid']
    base = NETWORK_PROFILES[ssid]
    speed = float(station.params.get('speed', base['speed']))
    dist = max(distance, 1.0)
    simulated_rssi = -40 - (10 * 4.5 * math.log10(dist)) 
    adjusted_sinr = base['sinr'] + (simulated_rssi + 50) / 2.0 
    signal_strength = max(0.1, (100 + simulated_rssi) / 60.0) 
    actual_rate = base['max_rate'] * signal_strength
    return [speed, actual_rate, base['delay'], adjusted_sinr, base['ber'], base['loss']]

def handover_decision_worker(station, access_points, stop_event):
    current_ap = None
    start_time = time.time()
    
    # Initialize the CSV log with headers
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'UMTS', 'GPRS', 'WLAN', '4G', '5G'])
    
    while not stop_event.is_set():
        predictions = {}
        for ap in access_points:
            dist = get_distance(station, ap)
            if dist > 30.0:
                predictions[ap] = 0.0
                continue
            ssid = ap.params['ssid']
            features = collect_network_parameters(station, ap, dist)
            pred_rate = models[ssid].predict([features])[0]
            predictions[ap] = max(0.0, pred_rate)

        best_ap = max(predictions, key=predictions.get)
        best_ssid = best_ap.params['ssid']
        
        # Log live metrics to CSV
        current_time = round(time.time() - start_time, 1)
        row = [current_time]
        for net in ['UMTS', 'GPRS', 'WLAN', '4G', '5G']:
            ap_obj = next((a for a in access_points if a.params['ssid'] == net), None)
            row.append(round(predictions.get(ap_obj, 0.0), 2))
            
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
        
        rates_summary = " | ".join([f"{ap.params['ssid']}: {rate:.0f}" for ap, rate in predictions.items()])
        info(f"\n[Telemetry] {rates_summary}\n")
        info(f"[Decision]  --> Selected Target: {best_ssid} ({predictions[best_ap]:.0f} kbps)\n")
        
        if current_ap != best_ap and predictions[best_ap] > 0:
            info(f"[*** Handover Executing ***] Migrating to {best_ssid}\n")
            station.pexec(f'iw dev {station.wintfs[0].name} disconnect')
            station.pexec(f'iw dev {station.wintfs[0].name} connect {best_ssid}')
            current_ap = best_ap
            
        time.sleep(2)

def start_vertical_handover(station, access_points):
    stop_event = threading.Event()
    worker = threading.Thread(
        target=handover_decision_worker,
        args=(station, access_points, stop_event),
        daemon=True
    )
    worker.start()
    return stop_event