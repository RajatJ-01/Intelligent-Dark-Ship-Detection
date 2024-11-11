import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import random

def visualize_ship_paths(dark_ship_index=None):
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('Black')  
    ax.set_facecolor('Black')

    colors = ['yellow', 'blue', 'purple', 'orange', 'green']

    paths = []
    offsets = [0.5, 1.0, 1.5, 2.0, 2.5]  

    
    for i in range(5):
        x = np.linspace(0.1, 0.9, 5) 
        y = 0.5 * np.sin(2 * np.pi * (x - 0.1) + i * np.pi / 6) + offsets[i]  
        paths.append((x, y))


    if dark_ship_index is not None:
        dark_ship_x = np.linspace(0.1, 0.9, 5)
        dark_ship_y = 0.5 * np.sin(2 * np.pi * (dark_ship_x - 0.1)) + 0.5 + 0.1 * np.random.randn(5) + offsets[dark_ship_index]

        turn_point = 3
        dark_ship_x_reverse = np.linspace(dark_ship_x[turn_point], dark_ship_x[turn_point] - 0.2, 2)  
        dark_ship_y_reverse = 0.5 * np.sin(2 * np.pi * (dark_ship_x_reverse - 0.1)) + 0.5 + 0.1 * np.random.randn(2) + offsets[dark_ship_index]

        y_shift = 0.3  
        dark_ship_y_reverse_shifted = dark_ship_y_reverse + y_shift

        dark_ship_x_full = np.concatenate([dark_ship_x[:turn_point], dark_ship_x_reverse])
        dark_ship_y_full = np.concatenate([dark_ship_y[:turn_point], dark_ship_y_reverse_shifted])

        paths[dark_ship_index] = (dark_ship_x_full, dark_ship_y_full)

    for i, (x, y) in enumerate(paths):
        vessel_name = f"Vessel_{i}"  
     
        ax.plot(x, y, color=colors[i], linewidth=2)

        
        for j in range(len(x) - 1):
            ax.plot(x[j], y[j], marker='s', color=colors[i], markersize=8)
            ax.text(x[j], y[j] + 0.1, 'AIS ON', color='white', fontsize=7, ha='center')

        
        ax.text(x[0], y[0] - 0.14, vessel_name, color=colors[i], fontsize=9, ha='center', fontweight='bold')

 
    if dark_ship_index is not None:
        ais_lost_index = len(paths[dark_ship_index][0]) - 1
        x, y = paths[dark_ship_index]
        ax.plot(x[ais_lost_index], y[ais_lost_index], marker='o', color='red', markersize=10)
        ax.text(x[ais_lost_index], y[ais_lost_index] + 0.1, 'AIS SIGNAL LOST', color='red', fontsize=10, fontweight='bold', ha='center')

        box = Rectangle((x[ais_lost_index] - 0.05, y[ais_lost_index] - 0.05), 0.1, 0.1, linewidth=1.5, edgecolor='red', facecolor='none')
        ax.add_patch(box)

    ax.axis('off')
    plt.show()
