import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
import threading
import cv2
import face_recognition
import pandas as pd
import serial
import os
import time
from datetime import datetime
import winsound
import serial
import serial.tools.list_ports
import time

# ----- CONFIG -----
USERS_CSV = "users.csv"
INTRUDER_DIR = "intruders"
AUTHORIZED_DIR = "authorized_faces"
ATTENDANCE_FILE = "attendance.csv"
MAX_UNAUTH_ATTEMPTS = 3

# create directories if not exist
os.makedirs(INTRUDER_DIR, exist_ok=True)
os.makedirs(AUTHORIZED_DIR, exist_ok=True)

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


# load users
if os.path.exists(USERS_CSV):
    users_df = pd.read_csv(USERS_CSV, dtype=str)
else:
    users_df = pd.DataFrame(columns=["name", "rfid", "image"])

user_map = {}
for _, row in users_df.iterrows():
    rfid = str(row["rfid"]).strip()
    name = row["name"]
    img_path = row["image"]
    try:
        enc = face_recognition.face_encodings(face_recognition.load_image_file(img_path))[0]
        user_map[rfid] = {"name": name, "encoding": enc}
    except Exception:
        print(f"[WARN] Failed to encode face for {name}")

# create attendance file if missing
if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Name", "RFID", "Date", "In Time", "Out Time"]).to_csv(ATTENDANCE_FILE, index=False)

unauth_attempts = {}

# ----- HELPER FUNCTIONS -----
def play_beep(frequency=700, duration=400):
    try:
        winsound.Beep(frequency, duration)
    except:
        pass


# ✅ NEW FIXED ATTENDANCE LOGIC
def mark_attendance(name, rfid):
    now = datetime.now()
    date_today = now.strftime("%m/%d/%Y")
    time_now = now.strftime("%I:%M:%S %p")

    if os.path.exists(ATTENDANCE_FILE):
        df = pd.read_csv(ATTENDANCE_FILE)
    else:
        df = pd.DataFrame(columns=["Name", "RFID", "Date", "In Time", "Out Time"])

    if not df.empty and "Date" in df.columns:
        df["Date"] = df["Date"].astype(str).str.replace("-", "/")

    existing = df[(df["Name"] == name) & (df["RFID"].astype(str) == str(rfid)) & (df["Date"] == date_today)]

    if existing.empty:
        new_row = {
            "Name": name,
            "RFID": rfid,
            "Date": date_today,
            "In Time": time_now,
            "Out Time": ""
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        print(f"[INFO] {name} checked IN at {time_now}")
    else:
        df.loc[existing.index, "Out Time"] = time_now
        print(f"[INFO] {name} checked OUT at {time_now}")

    df.to_csv(ATTENDANCE_FILE, index=False)


def capture_intruder_image():
    cap = cv2.VideoCapture(0)
    time.sleep(0.3)
    ret, frame = cap.read()
    if ret:
        path = os.path.join(INTRUDER_DIR, f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(path, frame)
        print(f"[ALERT] Intruder image saved: {path}")
    cap.release()


def verify_face(encoding, timeout=8):
    cap = cv2.VideoCapture(0)
    start = time.time()
    verified = False
    while time.time() - start < timeout:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encs = face_recognition.face_encodings(rgb)
        for e in encs:
            if True in face_recognition.compare_faces([encoding], e, tolerance=0.45):
                verified = True
                break
        cv2.imshow("Face Verification", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if verified:
            break
    cap.release()
    cv2.destroyAllWindows()
    return verified


def send_to_arduino(msg):
    if ser:
        ser.write((msg + "\n").encode())


# ----- GUI -----
class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teacher Attendance Panel")
        self.geometry("480x340")
        self.configure(bg="#eaf6ff")

        footer = ttk.Label(self, text="Developed by Abdullah Zahid",
                           font=("Segoe UI", 10, "italic"),
                           foreground="#555555")
        footer.pack(side="bottom", anchor="e", padx=10, pady=5)

        tk.Label(self, text="Smart Attendance System", font=("Segoe UI", 16, "bold"), bg="#eaf6ff").pack(pady=10)
        self.status_label = tk.Label(self, text="Please scan your RFID card", font=("Segoe UI", 12),
                                     bg="#eaf6ff", fg="blue")
        self.status_label.pack(pady=20)

        self.info_label = tk.Label(self, text="", font=("Segoe UI", 11), bg="#eaf6ff")
        self.info_label.pack(pady=5)

        tk.Button(self, text="Start Attendance", command=self.start_thread,
                  bg="#4CAF50", fg="white", font=("Segoe UI", 11), relief="raised").pack(pady=10)

        tk.Button(self, text="Manual RFID Entry", command=self.manual_rfid_entry,
                  bg="#2196F3", fg="white", font=("Segoe UI", 11), relief="raised").pack(pady=10)

    def start_thread(self):
        threading.Thread(target=self.attendance_loop, daemon=True).start()

    def attendance_loop(self):
        self.status_label.config(text="Waiting for card...", fg="black")
        while True:
            if ser and ser.in_waiting:
                uid = ser.readline().decode(errors="ignore").strip()
                if not uid:
                    continue
                print("[RFID]", uid)
                self.process_uid(uid)
            else:
                time.sleep(0.1)

    def manual_rfid_entry(self):
        uid = simpledialog.askstring("Manual RFID", "Enter RFID number:")
        if uid:
            print("[MANUAL RFID]", uid)
            self.process_uid(uid.strip())

    # ✅ UPDATED process_uid (combined + fixed)
    def process_uid(self, uid):
        uid = str(uid).strip()
        print("[RFID CHECK]", uid)

        if uid in user_map:
            user = user_map[uid]
            self.status_label.config(text=f"Recognized card: {user['name']}. Please look at the camera...", fg="blue")
            ok = verify_face(user["encoding"])

            if ok:
                mark_attendance(user["name"], uid)
                self.status_label.config(text=f"Welcome {user['name']}! Attendance marked.", fg="green")
                send_to_arduino("AUTHORIZED")
                play_beep(1000, 150)
                unauth_attempts[uid] = 0  # reset on success
            else:
                self.status_label.config(text="Face not recognized!", fg="red")
                send_to_arduino("UNAUTHORIZED")
                play_beep(600, 400)
                unauth_attempts[uid] = unauth_attempts.get(uid, 0) + 1
                print(f"[WARN] Unauthorized face attempt #{unauth_attempts[uid]} for {uid}")
                if unauth_attempts[uid] >= MAX_UNAUTH_ATTEMPTS:
                    capture_intruder_image()
                    unauth_attempts[uid] = 0
                    messagebox.showwarning("ALERT", "Unauthorized person detected! Intruder image saved.")
        else:
            self.status_label.config(text="Unknown RFID card!", fg="red")
            send_to_arduino("UNAUTHORIZED")
            play_beep(600, 400)
            unauth_attempts[uid] = unauth_attempts.get(uid, 0) + 1
            print(f"[WARN] Unauthorized RFID attempt #{unauth_attempts[uid]} for {uid}")
            if unauth_attempts[uid] >= MAX_UNAUTH_ATTEMPTS:
                capture_intruder_image()
                unauth_attempts[uid] = 0
                messagebox.showwarning("ALERT", "Unauthorized card detected! Intruder image saved.")


if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
