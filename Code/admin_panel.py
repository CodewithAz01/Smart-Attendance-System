# admin_panel.py
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox
import threading
import serial
import time
import cv2
import os
import pandas as pd
from datetime import datetime
import winsound  # Windows only
# Try to connect to serial
import serial
import serial.tools.list_ports
import time

# ----- CONFIG -----
ADMIN_PASSWORD = "admin123"  # change to your desired admin password
USERS_CSV = "users.csv"      # stores name, rfid, image_path
AUTHORIZED_DIR = "authorized_faces"
INTRUDER_DIR = "intruders"
RESET_AFTER_SCAN = True      # if True, Python will toggle DTR to reset Arduino after a scan

# ensure folders exist
os.makedirs(AUTHORIZED_DIR, exist_ok=True)
os.makedirs(INTRUDER_DIR, exist_ok=True)

import serial.tools.list_ports

def connect_arduino(baudrate=9600):
    """
    Automatically detect Arduino COM port and connect.
    """
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if ("Arduino" in port.description) or ("USB-SERIAL" in port.description) or ("CH340" in port.description):
            try:
                ser = serial.Serial(port.device, baudrate, timeout=1)
                time.sleep(2)
                print(f"[INFO] Connected automatically to {port.device}")
                print("[INFO] Resetting Arduino...")
                ser.setDTR(False)      # Drop DTR signal
                time.sleep(0.5)
                ser.setDTR(True)       # Re-enable DTR signal
                time.sleep(2)          # Wait for Arduino reboot
                print("[INFO] Arduino reset successfully.")
                return ser
            except Exception as e:
                print(f"[ERROR] Failed to connect on {port.device}: {e}")
    return None

# Try automatic connection first
ser = connect_arduino(9600)

# If not found, ask the user manually
if not ser:
    print("\n[WARN] Could not auto-detect Arduino.")
    print("Available COM ports:")
    for p in serial.tools.list_ports.comports():
        print(f" - {p.device}: {p.description}")
    port = input("Enter COM port manually (e.g., COM5): ")
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)
        print(f"[INFO] Connected manually to {port}")
        print("[INFO] Resetting Arduino...")
        ser.setDTR(False)      # Drop DTR signal
        time.sleep(0.5)
        ser.setDTR(True)       # Re-enable DTR signal
        time.sleep(2)          # Wait for Arduino reboot
        print("[INFO] Arduino reset successfully.")
    except Exception as e:
        print(f"[ERROR] Manual connection failed: {e}")
        ser = None



# ----- helper functions -----
def play_alert_long():
    try:
        winsound.Beep(700, 600)
    except Exception:
        pass

def play_alert_short():
    try:
        winsound.Beep(1000, 150)
    except Exception:
        pass

def read_rfid_block(timeout=15):
    """Wait for RFID UID from Arduino for `timeout` seconds. Returns UID string or None."""
    if ser is None:
        uid = simpledialog.askstring("RFID Missing", "Serial not connected. Enter RFID UID manually:")
        return uid
    start = time.time()
    ser.reset_input_buffer()
    while time.time() - start < timeout:
        line = ser.readline().decode(errors='ignore').strip()
        if not line:
            continue
        print("[DEBUG] Serial line:", line)  # For debugging
        # Accept either "CARD_UID:" prefixed or plain UID
        if "CARD_UID:" in line:
            uid = line.split(":")[1].strip()
            return uid
        elif line.isdigit() or len(line) > 3:
            # fallback: treat any non-empty numeric line as UID
            return line
    return None

def capture_face_image(save_path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Camera not found")
        return False
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow("Capture face - press SPACE to save or ESC to cancel", frame)
        key = cv2.waitKey(1)
        if key == 32:  # SPACE
            cv2.imwrite(save_path, frame)
            break
        elif key == 27:  # ESC
            cap.release()
            cv2.destroyAllWindows()
            return False
    cap.release()
    cv2.destroyAllWindows()
    return True

def save_user(name, rfid, image_path):
    # If the file doesn't exist or is empty, create a new one with proper columns
    if not os.path.exists(USERS_CSV) or os.stat(USERS_CSV).st_size == 0:
        df = pd.DataFrame(columns=["name", "rfid", "image"])
    else:
        try:
            df = pd.read_csv(USERS_CSV)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=["name", "rfid", "image"])

    # Append new record safely
    df = pd.concat([df, pd.DataFrame([{"name": name, "rfid": rfid, "image": image_path}])], ignore_index=True)

    # Save to CSV
    df.to_csv(USERS_CSV, index=False)
    print(f"[INFO] Saved user: {name} ({rfid}) to {USERS_CSV}")


def reset_arduino_serial():
    if ser is None:
        return
    try:
        ser.dtr = False
        time.sleep(0.4)
        ser.dtr = True
        time.sleep(2)
    except:
        pass

# ----- Tkinter UI -----
class AdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Panel")
        self.geometry("420x220")
        self.attempts = 0


        footer = ttk.Label(self, text="Developed by Abdullah Zahid",
                           font=("Segoe UI", 10, "italic"),
                           foreground="#555555")
        footer.pack(side="bottom", anchor="e", padx=10, pady=5)

        tk.Label(self, text="Smart Attendance - Admin Panel", font=("Segoe UI", 14)).pack(pady=10)
        admin_btn = tk.Button(self, text="Admin", width=20, command=self.admin_login)
        admin_btn.pack(pady=8)

        self.status_label = tk.Label(self, text="Ready", fg="green")
        self.status_label.pack(pady=8)

        reg_btn = tk.Button(self, text="Open Registration Window (for debugging)", command=self.open_register_window)
        reg_btn.pack(pady=6)

    def admin_login(self):
        pw = simpledialog.askstring("Admin Password", "Enter admin password:", show='*')
        if pw is None:
            return
        if pw == ADMIN_PASSWORD:
            self.attempts = 0
            self.open_register_window()
        else:
            self.attempts += 1
            messagebox.showerror("Wrong Password", f"Incorrect password ({self.attempts}/3)")
            if self.attempts >= 3:
                self.on_intruder_password_attempt()

    def on_intruder_password_attempt(self):
        self.status_label.config(text="Intruder detected! Capturing image...", fg="red")
        # take webcam photo and save
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = os.path.join(INTRUDER_DIR, f"intruder_pw_{ts}.jpg")
        cap = cv2.VideoCapture(0)
        time.sleep(0.5)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(img_path, frame)
        cap.release()
        cv2.destroyAllWindows()
        play_alert_long()
        messagebox.showwarning("Alert", f"Intruder captured and saved to:\n{img_path}")
        self.attempts = 0
        self.status_label.config(text="Ready", fg="green")

    def open_register_window(self):
        # small registration dialog
        reg = tk.Toplevel(self)
        reg.title("Register New Teacher")
        reg.geometry("380x380")

        tk.Label(reg, text="Teacher Name:").pack(pady=(12,0))
        name_entry = tk.Entry(reg, width=30); name_entry.pack()

        tk.Label(reg, text="Step 1: Scan RFID card now (or click 'Scan manually')").pack(pady=(10,0))
        uid_var = tk.StringVar()
        uid_label = tk.Label(reg, textvariable=uid_var, fg="blue")
        uid_label.pack()

        def scan_rfid_thread():
            uid_var.set("Waiting for RFID (10s)...")
            uid = read_rfid_block(timeout=10)
            if uid:
                uid_var.set(uid)
            else:
                uid_var.set("No RFID read")

        scan_btn = tk.Button(reg, text="Scan RFID (10s wait)", command=lambda: threading.Thread(target=scan_rfid_thread, daemon=True).start())
        scan_btn.pack(pady=6)

        def manual_scan():
            val = simpledialog.askstring("Manual UID", "Enter card UID manually:")
            if val:
                uid_var.set(val)
        manual_btn = tk.Button(reg, text="Scan manually", command=manual_scan)
        manual_btn.pack(pady=4)

        tk.Label(reg, text="Step 2: Capture face image (press SPACE).").pack(pady=(8,0))

        def do_register():
            name = name_entry.get().strip()
            uid = uid_var.get().strip()
            if not name or not uid:
                messagebox.showerror("Missing", "Provide name and RFID UID")
                return
            img_name = f"{name}.jpg"
            img_path = os.path.join(AUTHORIZED_DIR, img_name)
            ok = capture_face_image(img_path)
            if not ok:
                messagebox.showinfo("Cancelled", "Face capture cancelled")
                return
            save_user(name, uid, img_path)
            messagebox.showinfo("Registered", f"Registered {name} with UID {uid}")
            # optional: reset arduino to be safe
            reset_arduino_serial()
            reg.destroy()

        reg_btn = tk.Button(reg, text="Register Teacher", command=do_register, bg="#4CAF50", fg="white")
        reg_btn.pack(pady=(12,6), ipadx=10)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()
