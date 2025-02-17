import sys
import os
import subprocess
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor
from tkinter import Tk, filedialog, Frame, Listbox, Scrollbar, Button as TkButton
import tkinter as tk
import datetime

# Set new map size
MAP_SIZE = 276480

# List to store clicked points
clicked_points = []

# Initialize panning state
panning = False

# Load WebP Image
def load_webp():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select WebP Image", filetypes=[("WebP Files", "*.webp")])
    return file_path

# Update image in the GUI
def update_image():
    global img_array, ax, canvas
    img_path = load_webp()
    if img_path:
        image = Image.open(img_path).convert("L")  # Convert to grayscale
        img_array = np.array(image)
        ax.clear()
        ax.imshow(img_array, cmap='gray', extent=[0, img_array.shape[1], img_array.shape[0], 0])
        ax.set_title("Hover to See Coordinates")
        canvas.draw()

# Save coordinates
def save_coordinates():
    try:
        local_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cords")
        os.makedirs(local_folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(local_folder, f"cords_{timestamp}.txt")
        with open(file_path, "w") as file:
            for point in clicked_points:
                file.write(f"{point[0]}, {point[1]}\n")
        print(f"Coordinates saved to {file_path}")
    except PermissionError:
        print("Permission denied: Unable to save coordinates.")
    except Exception as e:
        print(f"Error saving coordinates: {e}")

# Convert pixel to world coordinates
def pixel_to_world(x, y):
    scale_x = MAP_SIZE / 1493
    scale_y = MAP_SIZE / 1493
    world_x = (x - img_array.shape[1] / 2) * scale_x
    world_y = (y - img_array.shape[0] / 2) * scale_y
    return world_x, world_y

# Handle mouse clicks
def on_click(event):
    global prev_x, prev_y, panning
    if event.button == 1 and event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        if 0 <= x < img_array.shape[1] and 0 <= y < img_array.shape[0]:
            world_x, world_y = pixel_to_world(x, y)
            clicked_points.append((world_x, world_y))
            ax.plot(x, y, 'ro')
            canvas.draw()
            listbox.insert(tk.END, f"({world_x:.2f}, {world_y:.2f})")
    elif event.button == 3:
        panning = True
        prev_x, prev_y = event.x, event.y

# Handle mouse release
def on_release(event):
    global panning
    if event.button == 3:
        panning = False

# Handle mouse motion for panning
def on_motion(event):
    global prev_x, prev_y, panning
    if panning and event.x is not None and event.y is not None:
        dx = (event.x - prev_x) * 0.5
        dy = (event.y - prev_y) * 0.5
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.set_xlim([x + dx for x in xlim])
        ax.set_ylim([y + dy for y in ylim])
        prev_x, prev_y = event.x, event.y
        canvas.draw()

# Handle zooming
def zoom(event):
    scale_factor = 1.2 if event.step > 0 else 0.8
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_center = (xlim[0] + xlim[1]) / 2
    y_center = (ylim[0] + ylim[1]) / 2
    new_xlim = [x_center + (x - x_center) * scale_factor for x in xlim]
    new_ylim = [y_center + (y - y_center) * scale_factor for y in ylim]
    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)
    canvas.draw()

# Initialize main Tkinter window
root = tk.Tk()
root.title("Coordinate Logger")

# Create Matplotlib figure
fig, ax = plt.subplots()
ax.set_title("Load an Image to Begin")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create frame for coordinate list
frame = Frame(root)
frame.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar = Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox = Listbox(frame, yscrollcommand=scrollbar.set, width=30)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox.yview)

# Add buttons
save_button = TkButton(root, text="Save Coordinates", command=save_coordinates)
save_button.pack(side=tk.BOTTOM, pady=5)

load_button = TkButton(root, text="Load Image", command=update_image)
load_button.pack(side=tk.BOTTOM, pady=5)

# Bind event handlers
canvas.mpl_connect("button_press_event", on_click)
canvas.mpl_connect("button_release_event", on_release)
canvas.mpl_connect("motion_notify_event", on_motion)
canvas.mpl_connect("scroll_event", zoom)

# Start Tkinter event loop
root.mainloop()
