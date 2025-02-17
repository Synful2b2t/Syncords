import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Cursor
from tkinter import Tk, filedialog, Frame, Listbox, Scrollbar, Button as TkButton
import tkinter as tk
import os
import datetime
import sys
import subprocess

# Ensure the script's directory is the working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Hide the CMD window on Windows when running as a script
def hide_cmd_window():
    if os.name == 'nt' and sys.stdout is not None:  # Running in a visible CMD window
        script = os.path.abspath(sys.argv[0])
        subprocess.Popen(["pythonw", script], close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
        sys.exit()  # Exit the current CMD process

hide_cmd_window()  # Call the function at the start

# Ensure all required rasterio modules are included for PyInstaller
import rasterio.vrt
import rasterio.sample
import rasterio.windows

# List to store clicked points
clicked_points = []
# Variables for panning
pan_start = None

def load_tif():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select TIF Image", filetypes=[("TIFF Files", "*.tif;*.tiff")])
    return file_path

def update_image():
    global image, transform, ax, canvas
    tif_path = load_tif()
    if tif_path:
        with rasterio.open(tif_path) as dataset:
            image = dataset.read(1)
            transform = dataset.transform
        
        ax.clear()
        ax.imshow(image, cmap='gray', extent=[0, image.shape[1], image.shape[0], 0])
        ax.set_title("Hover to See Coordinates")
        canvas.draw()

def pixel_to_world(x, y, transform):
    world_x, world_y = transform * (x, y)
    return world_x, world_y

def on_click(event):
    if event.button == 1 and event.xdata is not None and event.ydata is not None and 'image' in globals():
        x, y = int(event.xdata), int(event.ydata)
        if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
            world_x, world_y = pixel_to_world(x, y, transform)
            world_y = -world_y  # Flip Y coordinate
            clicked_points.append((world_x, world_y))
            ax.plot(x, y, 'ro')  # Mark clicked point on the image
            canvas.draw()
            listbox.insert(tk.END, f"({world_x:.2f}, {world_y:.2f})")

def zoom(event):
    scale_factor = 1.2 if event.step > 0 else 0.8  # Adjust zoom based on scroll direction
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

def on_close():
    root.quit()
    root.destroy()
    sys.exit()

root.protocol("WM_DELETE_WINDOW", on_close)

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

def save_coordinates():
    local_folder = os.path.join(script_dir, "cords")
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

def on_hover(event):
    if event.xdata is not None and event.ydata is not None and 'image' in globals():
        x, y = int(event.xdata), int(event.ydata)
        if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
            world_x, world_y = pixel_to_world(x, y, transform)
            world_y = -world_y  # Flip Y coordinate
            ax.set_title(f"World Coordinates: ({world_x:.2f}, {world_y:.2f})")
            canvas.draw()

cursor = Cursor(ax, useblit=True, color='red', linewidth=1)
canvas.mpl_connect("motion_notify_event", on_hover)
canvas.mpl_connect("button_press_event", on_click)
canvas.mpl_connect("scroll_event", zoom)

# Start Tkinter event loop
root.mainloop()
