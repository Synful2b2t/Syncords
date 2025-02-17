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

# Relaunch as a hidden process if running as .py (Windows only)
if sys.platform == "win32" and sys.argv[0].endswith(".py"):
    script_path = os.path.abspath(sys.argv[0])
    if not sys.executable.endswith("pythonw.exe"):  # Prevent infinite loop
        subprocess.Popen(["pythonw", script_path], close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
        sys.exit()

# Set new map size
MAP_SIZE = 276480  # Updated from 250000

# List to store clicked points
clicked_points = []

# Load WebP Image
def load_webp():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select WebP Image", filetypes=[("WebP Files", "*.webp")])
    return file_path

# Update image in the GUI
def update_image():
    global image, img_array, ax, canvas
    img_path = load_webp()
    if img_path:
        image = Image.open(img_path).convert("L")  # Convert to grayscale
        img_array = np.array(image)
        ax.clear()
        ax.imshow(img_array, cmap='gray', extent=[0, img_array.shape[1], img_array.shape[0], 0])
        ax.set_title("Hover to See Coordinates")
        canvas.draw()

# Convert pixel to world coordinates
def pixel_to_world(x, y):
    scale_x = 276480 / 1493
    scale_y = 276480 / 1493
    world_x = (x - img_array.shape[1] / 2) * scale_x
    world_y = (y - img_array.shape[0] / 2) * scale_y  # Flip Y-axis
    return world_x, world_y

# Handle mouse clicks
def on_click(event):
    if event.button == 1 and event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        if 0 <= x < img_array.shape[1] and 0 <= y < img_array.shape[0]:
            world_x, world_y = pixel_to_world(x, y)
            clicked_points.append((world_x, world_y))
            ax.plot(x, y, 'ro')
            canvas.draw()
            listbox.insert(tk.END, f"({world_x:.2f}, {world_y:.2f})")

# Handle mouse hover
def on_hover(event):
    if event.xdata is not None and event.ydata is not None:
        x, y = int(event.xdata), int(event.ydata)
        if 0 <= x < img_array.shape[1] and 0 <= y < img_array.shape[0]:
            world_x, world_y = pixel_to_world(x, y)
            ax.set_title(f"World Coordinates: ({world_x:.2f}, {world_y:.2f})")
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

# Save coordinates
def save_coordinates():
    local_folder = "cords"
    os.makedirs(local_folder, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(local_folder, f"cords_{timestamp}.txt")
    with open(file_path, "w") as file:
        for point in clicked_points:
            file.write(f"{point[0]}, {point[1]}\n")

save_button = TkButton(root, text="Save Coordinates", command=save_coordinates)
save_button.pack(side=tk.BOTTOM, pady=10)

load_button = TkButton(root, text="Load Image", command=update_image)
load_button.pack(side=tk.BOTTOM, pady=10)

# Enable interactive features
cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
canvas.mpl_connect("motion_notify_event", on_hover)
canvas.mpl_connect("button_press_event", on_click)
canvas.mpl_connect("scroll_event", zoom)

# Start Tkinter event loop
root.mainloop()
