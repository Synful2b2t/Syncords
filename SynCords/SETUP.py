import subprocess
import sys
import os
import traceback
import tkinter
from tkinter import messagebox

# We use psutil to check if syncords.py is already running
try:
    import psutil
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# List of required dependencies
dependencies = [
    "rasterio",
    "numpy",
    "matplotlib",
    "tkinter"
]

def are_dependencies_installed():
    """ Checks if all dependencies are installed, installs missing ones. """
    for package in dependencies:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing package: {package}")
            install_package(package)

def is_script_running(script_name):
    """ Returns True if the script is already running, False otherwise. """
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['cmdline'] and script_name in " ".join(proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def main():
    # Ensure dependencies are installed
    are_dependencies_installed()

    # Set the directory to the same folder as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "syncords.py")

    # Check if syncords.py is already running
    if is_script_running("syncords.py"):
        print("syncords.py is already running. Skipping launch.")
        return

    # Launch syncords.py if present
    if os.path.exists(script_path):
        subprocess.Popen([sys.executable, script_path], shell=True)
        sys.exit()  # Exit the script after launching
    else:
        error_msg = "Error: syncords.py not found!"
        print(error_msg)
        # Show an error message box if possible
        try:
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Error", error_msg)
        except Exception:
            pass
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        error_message = traceback.format_exc()
        # Write the error to a log file
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
        with open(log_path, "w") as f:
            f.write(error_message)
        # Optionally, show the error in a message box
        try:
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Error", error_message)
        except Exception:
            pass
        sys.exit(1)
