import os
import random
import cv2
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
from ultralytics import YOLO
import time
from datetime import datetime, timedelta

try:
    model = YOLO("my_custom_model.pt").cpu()
except Exception as e:
    messagebox.showerror("Error", f"Model loading failed: {str(e)}")
    exit()

BASE_MMSI = 1291
mmsi_dict = {}

def generate_mmsi():
    """Generate a random 9-digit MMSI number."""
    return f"{random.randint(100000000, 999999999)}"

def increase_lat_lon(lat, lon):
    """Increase the last four digits of latitude and longitude."""
    lat_increment = round(random.uniform(0.0001, 0.0005), 4) 
    lon_increment = round(random.uniform(0.0001, 0.0005), 4)
    new_lat = round(lat + lat_increment, 6)
    new_lon = round(lon + lon_increment, 6)
    return new_lat, new_lon

def generate_initial_coordinates(base_lat, base_lon, num_vessels):
    """Generate initial coordinates for vessels."""
    coords = []
    for _ in range(num_vessels):
        lat_offset = random.uniform(0, 0.0001) 
        lon_offset = random.uniform(0, 0.0001)
        coords.append((round(base_lat + lat_offset, 6), round(base_lon + lon_offset, 6)))
    return coords

def draw_boxes(image, boxes, ais_data):
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        mmsi = ais_data[i]["synthetic_data"]["mmsi"]
        color = (0, 255, 0) if ais_data[i]["status"] == "Active" else (0, 0, 255)
        label = f"{ais_data[i]['id']} (MMSI: {mmsi})"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

def detect_ships(image_path, label_display, tree, vessel_coords, timestamp, dark_ship_index=None):
    original_image = cv2.imread(image_path)
    if original_image is None:
        messagebox.showerror("Error", "Image not found or unable to load.")
        return None, None 

    results = model(original_image)
    if not results or len(results[0].boxes.xyxy) == 0:
        messagebox.showinfo("Result", "No ships detected.")
        return None, None  
    boxes = results[0].boxes.xyxy.cpu().numpy()
    num_boxes = len(boxes)

    ais_data = {}
    for i in range(num_boxes):
        vessel_id = f"Vessel_{i}"
        if vessel_id not in mmsi_dict:
            mmsi_dict[vessel_id] = generate_mmsi()

        ais_data[i] = {
            "id": vessel_id,
            "status": "Active", 
            "coordinates": boxes[i][:4],
            "synthetic_data": {
                "mmsi": mmsi_dict[vessel_id], 
                "speed": round(random.uniform(0, 30), 2),
                "heading": random.randint(0, 360),
                "latitude": round(vessel_coords[i][0], 6) if i < len(vessel_coords) else None,
                "longitude": round(vessel_coords[i][1], 6) if i < len(vessel_coords) else None
            },
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S")
        }
    
    if dark_ship_index is not None and dark_ship_index < num_boxes:
        ais_data[dark_ship_index]["status"] = "Inactive"  
    display_image = original_image.copy()
    draw_boxes(display_image, boxes, ais_data)

    tree.delete(*tree.get_children())
    for i in range(num_boxes):
        if i == dark_ship_index:
            tree.insert("", "end", values=( 
                ais_data[i]["id"],
                ais_data[i]["synthetic_data"]["mmsi"],
                "",
                "",
                "",
                "",
                ""
            ))
        else:
            tree.insert("", "end", values=( 
                ais_data[i]["id"],
                ais_data[i]["synthetic_data"]["mmsi"],
                ais_data[i]["synthetic_data"]["speed"],
                ais_data[i]["synthetic_data"]["heading"],
                ais_data[i]["synthetic_data"]["latitude"],
                ais_data[i]["synthetic_data"]["longitude"],
                ais_data[i]["timestamp"]
            ))

    update_image_display(label_display, display_image)

    return boxes, display_image  

def update_image_display(label_display, image):
    max_width, max_height = 800, 600
    height, width = image.shape[:2]
    scale = min(max_width / width, max_height / height)
    new_size = (int(width * scale), int(height * scale))
    image = cv2.resize(image, new_size)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    image_tk = ImageTk.PhotoImage(image_pil)

    label_display.config(image=image_tk)
    label_display.image = image_tk  
    label_display.update()

def process_images(image_paths, label_display, tree):
    vessel_coords = []
    base_lat = random.uniform(-90, 90)
    base_lon = random.uniform(-180, 180)
    
    
    vessel_coords = generate_initial_coordinates(base_lat, base_lon, 5)

    for i, image_path in enumerate(image_paths):
     
        for j in range(len(vessel_coords)):
            vessel_coords[j] = increase_lat_lon(vessel_coords[j][0], vessel_coords[j][1])

        base_timestamp = datetime.now() + timedelta(hours=i * 2)  
        boxes, _ = detect_ships(image_path, label_display, tree, vessel_coords, base_timestamp)
        
        if boxes is not None:
            time.sleep(5)
            messagebox.showinfo("Performing Scan", "Performing Scan ....... Checking for Dark Ship")

            if i == len(image_paths) - 1:
              
                dark_ship_index = random.randint(0, len(vessel_coords) - 1)
               
                ais_data = {k: {"status": "Active"} for k in range(len(vessel_coords))}
                ais_data[dark_ship_index]["status"] = "Inactive"  
                detect_ships(image_path, label_display, tree, vessel_coords, base_timestamp, dark_ship_index)
                messagebox.showinfo("Dark Ship Detected", f"Dark Ship Detected...: Vessel_{dark_ship_index}")

def select_images(label_display, tree):
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_paths:
        process_images(file_paths, label_display, tree)

root = tk.Tk()
root.title("Dark Ship Detection")
root.geometry("1000x600")
root.configure(bg="#f0f0f0")

label_title = ttk.Label(root, text="Dark Ship Detection", font=("Arial", 30), background="#f0f0f0")
label_title.pack(pady=20)

select_button = ttk.Button(root, text="Select Images", command=lambda: select_images(label_display, tree))
select_button.pack(pady=10)

frame_display = ttk.Frame(root)
frame_display.pack(side=tk.LEFT, padx=35)

label_display = ttk.Label(frame_display)
label_display.pack()

tree_frame = ttk.Frame(root, borderwidth=2, relief="groove")
tree_frame.pack(side=tk.RIGHT, padx=35, fill=tk.Y)

columns = ("ID", "MMSI", "SOG ", "Heading (°)", "Latitude", "Longitude", "Timestamp")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120)

tree.pack(fill=tk.BOTH, expand=True)

root.mainloop()
