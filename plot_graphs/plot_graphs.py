import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

plt.style.use('seaborn-v0_8-pastel') 

# 1. HARDCODE THE EXACT PATH to prevent any directory confusion
csv_path = '/home/wifi/Desktop/EDGEChallenge/telemetry.csv'

fig, axes = plt.subplots(5, 1, figsize=(10, 12), sharex=True)
fig.canvas.manager.set_window_title('Live Heterogeneous Network Prediction')

networks = ['UMTS', 'GPRS', 'WLAN', '4G', '5G']
colors = ['#5b9bd5', '#ed7d31', '#70ad47', '#ffc000', '#4472c4']

def animate(frame):
    # Always draw the base titles, even if waiting for data
    fig.suptitle('Vertical Handover Real-Time Telemetry\n(Waiting for simulation data...)', fontsize=16, fontweight='bold')
    for i, net in enumerate(networks):
        axes[i].set_title(f"{net} Prediction: -- kbps", loc='left', pad=5, fontsize=12, fontweight='bold')
        axes[i].set_ylabel('kbps')
        axes[i].grid(True, linestyle='--', alpha=0.7)
    axes[4].set_xlabel('Simulation Time (seconds)', fontsize=12)
    
    if not os.path.exists(csv_path):
        print(f"Waiting: Could not find {csv_path}")
        return
        
    try:
        df = pd.read_csv(csv_path)
        if len(df) < 2:
            return # Need at least 2 data points to draw a line
            
        times = df['Time']
        latest_data = df.iloc[-1]
        
        # Identify active connection
        best_net = max(networks, key=lambda n: latest_data.get(n, 0))
        best_rate = latest_data.get(best_net, 0)
        
        # Update main title with active data
        fig.suptitle(f'Vertical Handover Real-Time Telemetry\nActive Target: {best_net} ({best_rate:,.0f} kbps)', 
                     fontsize=16, fontweight='bold', color='darkred')
        
        for i, net in enumerate(networks):
            axes[i].clear()
            axes[i].plot(times, df[net], color=colors[i], linewidth=2.5)
            axes[i].fill_between(times, df[net], color=colors[i], alpha=0.3)
            
            axes[i].set_ylabel('kbps')
            
            current_val = latest_data.get(net, 0)
            if net == best_net and current_val > 0:
                title_text = f"{net} Prediction: {current_val:,.0f} kbps [ACTIVE]"
                title_color = '#c00000' 
            else:
                title_text = f"{net} Prediction: {current_val:,.0f} kbps"
                title_color = 'black'
                
            axes[i].set_title(title_text, loc='left', pad=5, fontsize=12, fontweight='bold', color=title_color)
            axes[i].grid(True, linestyle='--', alpha=0.7)
            axes[i].margins(y=0.2)
            
        axes[4].set_xlabel('Simulation Time (seconds)', fontsize=12)
        plt.tight_layout()
        
    except PermissionError:
        print("[!] Permission Denied: Cannot read telemetry.csv. Run 'sudo chmod 777 telemetry.csv' in the terminal.")
    except Exception as e:
        # Catch empty file errors silently as the simulation writes to it
        pass

ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)
plt.tight_layout()
plt.show()