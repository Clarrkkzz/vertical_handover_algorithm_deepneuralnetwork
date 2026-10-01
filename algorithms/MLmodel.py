import os
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import joblib

current_dir = os.path.dirname(os.path.abspath(__file__))

baselines = {
    'UMTS': {'X': [3.0, 1024.0, 20.0, 18.0, 3.0, 0.005],     'y': 2048.0},
    'GPRS': {'X': [3.0, 115.0, 30.0, 16.0, 10.0, 0.009],      'y': 300.0},
    'WLAN': {'X': [3.0, 51200.0, 7.0, 22.0, 7.0, 0.002],     'y': 102400.0},
    '4G':   {'X': [3.0, 20480.0, 15.0, 20.0, 0.8, 0.001],     'y': 102400.0},
    '5G':   {'X': [3.0, 102400.0, 1.0, 25.0, 0.01, 0.0001],   'y': 512000.0}
}

def generate_samples(base_x, base_y, n_samples=100):
    np.random.seed(42)
    noise = np.random.uniform(0.90, 1.10, (n_samples, len(base_x)))
    X = base_x * noise
    y = base_y * np.random.uniform(0.95, 1.05, n_samples)
    return X, y

def train_and_save():
    for net, data in baselines.items():
        X, y = generate_samples(np.array(data['X']), data['y'])
        model = make_pipeline(
            StandardScaler(),
            MLPRegressor(hidden_layer_sizes=(6,), activation='logistic', solver='lbfgs', max_iter=5000)
        )
        model.fit(X, y)
        joblib.dump(model, os.path.join(current_dir, f'{net}_bp_model.pkl'))
        print(f"[+] {net:4s} Model Saved! Expected: ~{data['y']:8.1f} | Tested: {model.predict([data['X']])[0]:8.1f}")

if __name__ == '__main__':
    train_and_save()
