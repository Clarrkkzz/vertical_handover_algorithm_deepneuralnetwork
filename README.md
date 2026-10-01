# Heterogeneous Wireless Network Vertical Handover Simulation

A real-time simulation and visualization framework for **Vertical Handover Decision Engines** in next-generation heterogeneous wireless networks (UMTS, GPRS, WLAN, 4G, and 5G). This project models user mobility using Mininet-WiFi and evaluates optimal network connections dynamically using trained Back-Propagation (BP) Neural Networks.

## Project Structure


EDGEChallenge/
├── algorithms/
│   ├── MLmodel.py          # Generates and trains the 5 BP neural network models
│   ├── UMTS_bp_model.pkl   # Saved BP model for UMTS (3G)
│   ├── GPRS_bp_model.pkl   # Saved BP model for GPRS (2G)
│   ├── WLAN_bp_model.pkl   # Saved BP model for WLAN (Wi-Fi)
│   ├── 4G_bp_model.pkl     # Saved BP model for 4G LTE
│   └── 5G_bp_model.pkl     # Saved BP model for 5G
├── movement/
│   └── verticalhandover.py # Real-time telemetry collection, distance-based signal degradation, and CSV logging
├── topologies/
│   └── topologies.py       # Mininet-WiFi simulation environment and RandomWayPoint mobility
├── plot_graphs.py          # Real-time Matplotlib live-dashboard visualizer
├── telemetry.csv           # Live data bridge between emulation and graphs
└── requirements.txt        # Project dependencies


## Heterogeneous Wireless Network Vertical Handover Simulation

For ubuntu
sudo apt install python3-numpy python3-scikit-learn python3-joblib python3-pandas python3-matplotlib -y

Or via pip
pip install -r requirements.txt

## How to run the simulation 

### To start the simulation: 
sudo python3 topologies/topologies.py

### To run the graph:
sudo chmod 777 telemetry.csv  # Fixes any root permission locks on the data file
python3 plot_graphs.py

## How the Neural Network & Handover Engine Works

### 1. The Multi-Attribute Feature Vector
The system evaluates five distinct Back-Propagation (BP) neural networks (one for each network architecture: UMTS, GPRS, WLAN, 4G, 5G). Every few seconds, the background thread collects a 6-feature attribute vector for each access point:
* **Speed:** User terminal velocity ($m/s$).
* **Max Transmission Rate:** Theoretical peak bandwidth of the network type.
* **Delay:** Propagation and queuing latency ($ms$).
* **SINR:** Signal-to-Interference-plus-Noise Ratio (dynamically degraded based on real-time Euclidean distance using a log-distance propagation model).
* **BER:** Bit Error Rate.
* **Packet Loss Rate:** Environmental transmission loss ratio.

### 2. Standardization & Prediction Pipeline
Each network model uses a scikit-learn pipeline combining a **`StandardScaler`** (to normalize vastly different input ranges, e.g., transmission rates in tens of thousands vs. packet loss fractions) with an **`MLPRegressor`** (Back-Propagation Neural Network configured with a 6-6-1 topology). 

### 3. Physical Boundary & Handover Logic
* **Distance Hard Limit:** As the station (`sta1`) moves via `RandomWayPoint`, the script tracks its live coordinates. If the station moves further than **30 meters** from an access point, that network's predicted rate drops to `0 kbps` to simulate complete signal loss.
* **Decision Making:** The engine queries all five models simultaneously, selects the network yielding the highest predicted throughput, and triggers an automated network interface migration (`iw dev ... connect`) if a superior connection is found.