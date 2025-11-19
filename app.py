import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import cv2
import datetime
import os
import time
import threading

root = tk.Tk()
root.title("Posture Detection System")
root.geometry("1000x700")

process = None
saved_images_dir = "saved_images"
camera_in_use = False

if not os.path.exists(saved_images_dir):
    os.makedirs(saved_images_dir)

def run_posture_detection():
    global process, camera_in_use
    if process is None or process.poll() is not None:
        try:
            process = subprocess.Popen(["python", "MediaPipePoseTutorial.py"])
            camera_in_use = True
            print("Pose detection started.")
            update_status("✓ Pose detection RUNNING - Press 'S' in the camera window to save images with pose overlay")
            
            # Check if process is still running after 2 seconds
            root.after(2000, check_process_status)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start pose detection:\n{str(e)}")
            camera_in_use = False
    else:
        messagebox.showinfo("Info", "Pose detection is already running!")

def check_process_status():
    """Check if the MediaPipe process is still running"""
    global process, camera_in_use
    if process and process.poll() is not None:
        camera_in_use = False
        update_status("❌ Pose detection stopped unexpectedly")
        messagebox.showwarning("Process Stopped", "Pose detection stopped unexpectedly. Check the console for errors.")

def stop_posture_detection():
    global process, camera_in_use
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        camera_in_use = False
        print("Pose detection stopped.")
        process = None
        update_status("✓ Pose detection STOPPED")
        time.sleep(1)
    else:
        messagebox.showinfo("Info", "No active pose detection running.")

def save_raw_image():
    """Capture raw image from camera (without pose detection)"""
    global camera_in_use
    
    if camera_in_use:
        messagebox.showwarning(
            "Camera in Use", 
            "Pose detection is currently using the camera.\n\n"
            "Please STOP pose detection first to use this feature."
        )
        return
    
    cap = None
    try:
        cap = cv2.VideoCapture(0)
        time.sleep(0.5)
        
        if not cap.isOpened():
            messagebox.showerror("Error", "Camera not found!")
            return

        ret, frame = cap.read()
        
        if ret and frame is not None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"raw_capture_{timestamp}.jpg"
            filepath = os.path.join(saved_images_dir, filename)
            
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            messagebox.showinfo("Saved", f"✓ Raw image saved!\n\nFilename: {filename}\nLocation: {saved_images_dir}/")
            print(f"Raw image saved: {filepath}")
        else:
            messagebox.showerror("Error", "Failed to capture image from camera!")
            
    except Exception as e:
        messagebox.showerror("Error", f"Camera error: {str(e)}")
    finally:
        if cap:
            cap.release()

def show_save_instructions():
    """Show detailed instructions for saving pose images"""
    instructions = """
📸 HOW TO SAVE IMAGES WITH POSE DETECTION:

1. Click 'START POSE DETECTION' button
2. A NEW WINDOW will open with camera feed
3. In that camera window:
   • Press 'S' key to save image WITH pose overlay
   • Press 'Q' key to close the window
4. Images are automatically saved to 'saved_images' folder

🖼️ Images will include:
   • Pose landmarks and connections
   • Angle measurements
   • Rep counter
   • Stage information

⚠️ Important: Press 'S' in the CAMERA WINDOW, not here!
    """
    messagebox.showinfo("Save Instructions", instructions)

def view_saved_images():
    """Open the saved images directory"""
    try:
        if os.path.exists(saved_images_dir):
            # List files in the directory
            files = os.listdir(saved_images_dir)
            if files:
                if os.name == 'nt':  # Windows
                    os.startfile(saved_images_dir)
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.call(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', saved_images_dir])
                update_status(f"✓ Opened saved images folder ({len(files)} images)")
            else:
                messagebox.showinfo("Info", "Saved images folder is empty.")
        else:
            messagebox.showinfo("Info", "No saved images directory found.")
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open directory: {str(e)}")

def check_saved_images():
    """Check how many images are in the saved_images folder"""
    if os.path.exists(saved_images_dir):
        files = [f for f in os.listdir(saved_images_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        return len(files)
    return 0

# -------------------- UI SETUP --------------------
header = tk.Frame(root, bg="#2E86AB", height=80)
header.pack(fill="x")

title = tk.Label(header, text="🧘 Posture Detection System", 
                 bg="#2E86AB", fg="white", 
                 font=("Arial", 24, "bold"))
title.pack(pady=15)

# Main content
content = tk.Frame(root, bg="white")
content.pack(fill="both", expand=True, padx=20, pady=20)

# Welcome section
welcome_frame = tk.Frame(content, bg="white")
welcome_frame.pack(fill="x", pady=10)

tk.Label(welcome_frame, text="Welcome to Posture Detection", 
         bg="white", font=("Arial", 18, "bold")).pack(anchor="w")

tk.Label(welcome_frame, 
         text="This system uses MediaPipe for real-time pose detection and analysis.", 
         bg="white", font=("Arial", 12), justify="left").pack(anchor="w", pady=5)

# Instructions with better formatting
instructions_text = """
🎯 QUICK START GUIDE:

1. START POSE DETECTION - Launches the camera with pose tracking
2. In the camera window, press 'S' to save images WITH pose overlay
3. Press 'Q' in camera window to close it
4. Use VIEW SAVED to see your captured images

📁 All images are saved in: saved_images/ folder
"""
instructions_label = tk.Label(content, text=instructions_text, 
                             bg="white", font=("Arial", 11), 
                             justify="left", fg="#2C3E50")
instructions_label.pack(anchor="w", pady=15)

# Buttons frame
btn_frame = tk.Frame(content, bg="white")
btn_frame.pack(pady=30)

# Row 1 - Main controls
tk.Button(btn_frame, text="🚀 START POSE DETECTION", 
          font=("Arial", 14, "bold"), bg="#27AE60", fg="white", 
          width=25, height=2, 
          command=run_posture_detection).grid(row=0, column=0, padx=10, pady=10)

tk.Button(btn_frame, text="🛑 STOP POSE DETECTION", 
          font=("Arial", 14, "bold"), bg="#E74C3C", fg="white", 
          width=25, height=2, 
          command=stop_posture_detection).grid(row=0, column=1, padx=10, pady=10)

# Row 2 - Image controls
tk.Button(btn_frame, text="📸 SAVE RAW IMAGE", 
          font=("Arial", 12), bg="#3498DB", fg="white", 
          width=25, height=2, 
          command=save_raw_image).grid(row=1, column=0, padx=10, pady=10)

tk.Button(btn_frame, text="📁 VIEW SAVED IMAGES", 
          font=("Arial", 12), bg="#F39C12", fg="white", 
          width=25, height=2, 
          command=view_saved_images).grid(row=1, column=1, padx=10, pady=10)

# Row 3 - Help button
tk.Button(btn_frame, text="❓ HOW TO SAVE POSE IMAGES", 
          font=("Arial", 12, "bold"), bg="#9B59B6", fg="white", 
          width=52, height=2, 
          command=show_save_instructions).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Status bar
status_frame = tk.Frame(root, bg="#34495E", height=40)
status_frame.pack(fill="x", side="bottom")

status_label = tk.Label(status_frame, 
                       text="✅ Ready - Click 'START POSE DETECTION' to begin", 
                       bg="#34495E", fg="white", font=("Arial", 11))
status_label.pack(side="left", padx=15, pady=8)

image_count_label = tk.Label(status_frame, 
                            text=f"📷 Saved images: {check_saved_images()}", 
                            bg="#34495E", fg="white", font=("Arial", 11))
image_count_label.pack(side="right", padx=15, pady=8)

def update_status(message):
    status_label.config(text=message)
    image_count_label.config(text=f"📷 Saved images: {check_saved_images()}")
    root.update()

# Auto-refresh image count every 5 seconds
def refresh_image_count():
    image_count_label.config(text=f"📷 Saved images: {check_saved_images()}")
    root.after(5000, refresh_image_count)

refresh_image_count()

root.mainloop()