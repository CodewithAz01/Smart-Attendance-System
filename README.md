# 🎓 Smart Attendance System using RFID & Face Recognition

A secure and intelligent attendance management system that combines **RFID authentication**, **Face Recognition**, and **Arduino-based access control** to provide reliable teacher attendance tracking.

Developed as a personal learning project to explore Computer Vision, Embedded Systems, Serial Communication, and GUI Application Development.

---

## 🚀 Features

### 👨‍🏫 Teacher Registration

* Register teachers through the Admin Panel.
* Assign RFID cards to teachers.
* Capture and store teacher face images.
* Save teacher information in a CSV database.

### 🎫 RFID Authentication

* RFID card scanning using Arduino and RC522 RFID module.
* Automatic Arduino COM port detection.
* Manual COM port selection if auto-detection fails.

### 🤖 Face Recognition Verification

* Face verification after RFID authentication.
* Attendance marked only when RFID and Face Recognition both match.
* Prevents proxy attendance.

### 📊 Attendance Dashboard

* View attendance records in real time.
* Displays:

  * Teacher Name
  * RFID Number
  * Date
  * In Time
  * Out Time
* Refresh dashboard instantly.

### 🔒 Security Features

* Intruder detection system.
* Captures image after multiple unauthorized attempts.
* Stores intruder images automatically.
* Admin password protection.
* Audio alerts for unauthorized access.

### ⏰ Attendance Tracking

* First scan → Marks **IN Time**
* Second scan → Marks **OUT Time**
* Stores attendance records in CSV format.

---

# 🏗️ Project Architecture

RFID Card
↓
Arduino UNO + RC522
↓ Serial Communication
Python Application
↓
Face Recognition Verification
↓
Attendance Database (CSV)
↓
Dashboard & Reports

---

# 📂 Project Structure

Smart-Attendance-System/

├── main.py

├── admin_panel.py

├── attendence.py

├── dashboard.py

├── users.csv

├── attendance.csv

├── authorized_faces/

│ ├── teacher1.jpg

│ ├── teacher2.jpg

│ └── ...

├── intruders/

│ ├── intruder_001.jpg

│ ├── intruder_002.jpg

│ └── ...


---

# 🛠️ Hardware Requirements

* Arduino UNO
* RC522 RFID Reader
* RFID Cards / Tags
* USB Cable
* Webcam
* Computer/Laptop

---

# 💻 Software Requirements

* Python 3.10+
* Arduino IDE
* Windows OS (recommended)

---

# 📦 Python Libraries Used

## GUI

* tkinter
* ttk
* ttkbootstrap

## Computer Vision

* opencv-python
* face_recognition

## Data Handling

* pandas

## Serial Communication

* pyserial

## Date & Time

* datetime

## System Utilities

* os
* threading
* time
* winsound

---

# 📥 Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/Smart-Attendance-System.git
```

Move into project directory:

```bash
cd Smart-Attendance-System
```

Install dependencies:

```bash
pip install pandas
pip install pyserial
pip install opencv-python
pip install face_recognition
pip install ttkbootstrap
```

---

# ▶️ Running the Project

Start the main launcher:

```bash
python main.py
```

The launcher provides:

* Administrative Panel
* Teacher Attendance Panel
* Dashboard

---

# 👨‍💼 Admin Panel

Admin functionalities:

* Register Teachers
* Scan RFID Cards
* Capture Face Images
* Store Teacher Records
* Password Protected Access

Default Admin Password:

```text
admin123
```

---

# 👩‍🏫 Teacher Attendance Workflow

1. Teacher scans RFID card.
2. System identifies RFID.
3. Camera starts Face Verification.
4. Face is matched with stored image.
5. Attendance is recorded.
6. IN or OUT time is updated automatically.

---

# 📊 Attendance Format

attendance.csv

| Name           | RFID      | Date       | In Time  | Out Time |
| -------------- | --------- | ---------- | -------- | -------- |
| Abdullah Zahid | 144933146 | 10/19/2025 | 08:00 AM | 04:00 PM |

---

# 🔐 Security System

If an unauthorized user:

* Uses an unknown RFID card
* Fails face verification multiple times
* Attempts unauthorized access

The system:

* Triggers alert sound
* Captures intruder image
* Saves evidence in intruders folder

---

# 🔮 Future Improvements

* MySQL Database Integration
* Web-Based Dashboard
* Email Notifications
* Cloud Attendance Storage
* AI-Based Attendance Analytics
* Mobile Application Support
* QR Code Attendance System
* Face Recognition Attendance Portal

---

# 📸 Screenshots

Add screenshots of:

* Main Menu
* Admin Panel
* Attendance Window
* Dashboard
* Intruder Detection

---

# 👨‍💻 Author

Abdullah Zahid

Computer Science Student

Passionate about:

* Artificial Intelligence
* Computer Vision
* Embedded Systems
* Full Stack Development
* Automation Systems

---

# 📜 License

This project is developed for educational and portfolio purposes.

Feel free to fork, modify, and improve the project.

# 🚀 Created by Abdullah Zahid

⭐ If you found this project useful, please give it a star on GitHub.
