# Heterogeneous Wireless Network Vertical Handover Simulation

A real-time simulation and visualization framework for **Vertical Handover Decision Engines (VHDEs)** in heterogeneous wireless networks.

This project uses **Mininet-WiFi** to model user mobility across multiple wireless network technologies and dynamically evaluate network connections using trained **Back-Propagation (BP) Neural Networks**.

## Supported Networks

* **UMTS (3G)**
* **GPRS (2G)**
* **WLAN (Wi-Fi)**
* **4G LTE**
* **5G**

---

## Project Structure

```text
EDGEChallenge/
│
├── algorithms/
│   ├── MLmodel.py              # Generates and trains the 5 BP neural networks
│   ├── UMTS_bp_model.pkl       # Trained UMTS model
│   ├── GPRS_bp_model.pkl       # Trained GPRS model
│   ├── WLAN_bp_model.pkl       # Trained WLAN model
│   ├── 4G_bp_model.pkl         # Trained 4G model
│   └── 5G_bp_model.pkl         # Trained 5G model
│
├── movement/
│   └── verticalhandover.py     # Telemetry collection, signal degradation,
│                               # and CSV logging
│
├── topologies/
│   └── topologies.py           # Mininet-WiFi topology and mobility simulation
│
├── plot_graphs.py              # Real-time Matplotlib dashboard
├── telemetry.csv               # Telemetry data shared with the visualizer
└── requirements.txt            # Python dependencies
```

---

# Installation

## Requirements

The simulation is designed to run on **Ubuntu** with:

* Python 3
* Mininet-WiFi
* NumPy
* Scikit-learn
* Joblib
* Pandas
* Matplotlib

## Install Python Dependencies

### Option 1: Using apt

```bash
sudo apt install python3-numpy python3-scikit-learn python3-joblib python3-pandas python3-matplotlib -y
```

### Option 2: Using pip

```bash
pip install -r requirements.txt
```

> **Note:** Mininet-WiFi must be installed separately if it is not already available on your system.

---

# Running the Simulation

The project consists of two main processes:

1. **Mininet-WiFi simulation**
2. **Real-time graph visualizer**

## 1. Start the Mininet-WiFi Simulation

From the project root directory:

```bash
sudo python3 topologies/topologies.py
```

This starts the wireless network simulation and begins collecting telemetry from the mobile station.

## 2. Start the Real-Time Graph

Open a **separate terminal** and run:

```bash
python3 plot_graphs.py
```

If the telemetry file has permission issues because the simulation was started with `sudo`, run:

```bash
sudo chmod 777 telemetry.csv
```

Then:

```bash
python3 plot_graphs.py
```

---

# How the Neural Network & Handover Engine Works

The handover engine continuously evaluates the available networks and determines which network should provide the connection.

The system consists of three main stages:

```text
User Mobility
      │
      ▼
Telemetry Collection
      │
      ▼
Feature Vector
      │
      ▼
5 BP Neural Networks
      │
      ▼
Predicted Throughput
      │
      ▼
Best Available Network
      │
      ▼
Vertical Handover
```

## 1. Multi-Attribute Feature Vector

Every few seconds, the background telemetry process collects a **6-feature attribute vector** for each available access point.

The feature vector consists of:

| Feature                       | Description                                   |
| ----------------------------- | --------------------------------------------- |
| **Speed**                     | User terminal velocity in m/s                 |
| **Maximum Transmission Rate** | Theoretical peak bandwidth of the network     |
| **Delay**                     | Network propagation and queuing latency in ms |
| **SINR**                      | Signal-to-Interference-plus-Noise Ratio       |
| **BER**                       | Bit Error Rate                                |
| **Packet Loss Rate**          | Ratio of packets lost during transmission     |

The resulting feature vector is:

```text
[Speed, Max Transmission Rate, Delay, SINR, BER, Packet Loss Rate]
```

### Signal Degradation

The signal quality of each access point changes according to the station's distance from it.

The simulation uses a **log-distance propagation model** to dynamically degrade the SINR as the station moves away from an access point.

This allows the handover engine to react to changing wireless conditions during the simulation.

---

## 2. Standardization & Prediction Pipeline

Each network model uses a scikit-learn pipeline containing:

* `StandardScaler`
* `MLPRegressor`

The neural network uses a **6-6-1 architecture**:

```text
6 Input Features
       │
       ▼
6 Hidden Neurons
       │
       ▼
1 Output
```

In simplified form:

```text
6 → 6 → 1
```

The output represents the model's predicted network throughput.

### Standardization

The `StandardScaler` normalizes the input features before they are passed to the neural network.

This is necessary because the features have significantly different numerical ranges.

For example:

```text
Maximum Transmission Rate → Large values
Packet Loss Rate          → Small fractional values
Delay                     → Milliseconds
SINR                       → Signal quality value
```

The prediction pipeline is therefore:

```text
Raw Features
     │
     ▼
StandardScaler
     │
     ▼
MLPRegressor
     │
     ▼
Predicted Throughput
```

---

## 3. Physical Boundary & Handover Logic

The simulation applies a **30-meter distance limit** to each access point.

If the station moves more than 30 meters away from an access point:

```text
Distance > 30 meters
        │
        ▼
Network considered unavailable
        │
        ▼
Predicted throughput = 0 kbps
```

This provides a hard physical boundary for the simulated wireless networks.

### Network Selection

The handover engine queries all five neural network models and obtains a predicted throughput for each network:

```text
UMTS → Predicted Throughput
GPRS → Predicted Throughput
WLAN → Predicted Throughput
4G   → Predicted Throughput
5G   → Predicted Throughput
```

The engine then selects the network with the highest predicted throughput among the networks that are currently available.

---

## 4. Vertical Handover

When the handover engine determines that another network should be used, it triggers a network interface migration using:

```bash
iw dev ... connect
```

This allows the simulation to demonstrate **vertical handovers** between different wireless technologies.

For example:

```text
WLAN → 5G
5G   → 4G
4G   → UMTS
UMTS → GPRS
```

The actual handover sequence depends on the user's mobility and the network conditions generated during the simulation.

---

# Simulation Workflow

The complete system operates as follows:

```text
┌──────────────────────┐
│    Mininet-WiFi      │
│    Network Topology  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   RandomWayPoint     │
│      Mobility        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Telemetry Collection │
│                      │
│ Speed                │
│ Transmission Rate    │
│ Delay                │
│ SINR                 │
│ BER                  │
│ Packet Loss          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   5 BP Neural        │
│      Networks        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Predicted Throughput │
│      Comparison      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Handover Decision   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Network Interface    │
│      Migration       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    telemetry.csv     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Real-Time Graph     │
│     Visualizer       │
└──────────────────────┘
```

---

# Files and Their Responsibilities

| File                           | Purpose                                                                            |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| `algorithms/MLmodel.py`        | Generates and trains the BP neural network models                                  |
| `algorithms/UMTS_bp_model.pkl` | Trained UMTS model                                                                 |
| `algorithms/GPRS_bp_model.pkl` | Trained GPRS model                                                                 |
| `algorithms/WLAN_bp_model.pkl` | Trained WLAN model                                                                 |
| `algorithms/4G_bp_model.pkl`   | Trained 4G model                                                                   |
| `algorithms/5G_bp_model.pkl`   | Trained 5G model                                                                   |
| `movement/verticalhandover.py` | Collects telemetry, calculates signal degradation, and performs handover decisions |
| `topologies/topologies.py`     | Creates the Mininet-WiFi topology and mobility model                               |
| `plot_graphs.py`               | Displays telemetry and simulation results in real time                             |
| `telemetry.csv`                | Data bridge between the simulation and visualization                               |
| `requirements.txt`             | Lists the required Python packages                                                 |

---

# Quick Start

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Start the Simulation

```bash
sudo python3 topologies/topologies.py
```

## 3. Fix Telemetry Permissions

If required:

```bash
sudo chmod 777 telemetry.csv
```

## 4. Start the Visualizer

In a separate terminal:

```bash
python3 plot_graphs.py
```

---

# Technologies Used

* **Python**
* **Mininet-WiFi**
* **scikit-learn**
* **MLPRegressor**
* **NumPy**
* **Pandas**
* **Matplotlib**
* **Joblib**
* **Linux Wireless Tools (`iw`)**

---

# Project Goal

The goal of this project is to simulate and visualize **machine-learning-based vertical handover decisions** in heterogeneous wireless networks.

The system combines:

* Real-time user mobility
