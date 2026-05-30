import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import os
import sys
import ttkbootstrap as tb

# Path to your scripts (update if needed)
ADMIN_PANEL = "admin_panel.py"
TEACHER_ATTENDANCE = "attendence.py"
DASHBOARD = "dashboard.py"

class MainApp(tb.Window):
    def __init__(self):
        super().__init__(title="🌟 Smart Attendance System", themename="superhero")
        self.geometry("550x550")
        self.configure(bg="#1f1f2e")

        footer = ttk.Label(self, text="Developed by Abdullah Zahid",
                           font=("Segoe UI", 10, "italic"),
                           foreground="#555555")
        footer.pack(side="bottom", anchor="e", padx=10, pady=5)

        # Header
        tk.Label(self, text="🌸 Smart Attendance System", font=("Segoe UI", 24, "bold"), fg="#ffdd57", bg="#1f1f2e").pack(pady=30)

        btn_frame = tk.Frame(self, bg="#1f1f2e")
        btn_frame.pack(pady=20)

        # Buttons with colors and hover effects
        self.create_button(btn_frame, "🛠️ Administrative Panel", "#4CAF50", self.open_admin)
        self.create_button(btn_frame, "👩‍🏫 Teacher Attendance", "#2196F3", self.open_attendance)
        self.create_button(btn_frame, "📊 Dashboard", "#ff5722", self.open_dashboard)

    def create_button(self, parent, text, bg_color, command):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 16, "bold"), fg="white", bg=bg_color, width=30, height=2, relief="raised", command=command)
        btn.pack(pady=12)

        # Hover effect
        def on_enter(e):
            btn.config(bg="white", fg=bg_color)

        def on_leave(e):
            btn.config(bg=bg_color, fg="white")

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def open_admin(self):
        if os.path.exists(ADMIN_PANEL):
            subprocess.Popen([sys.executable, ADMIN_PANEL])
        else:
            messagebox.showerror("Error", f"{ADMIN_PANEL} not found!")

    def open_attendance(self):
        if os.path.exists(TEACHER_ATTENDANCE):
            subprocess.Popen([sys.executable, TEACHER_ATTENDANCE])
        else:
            messagebox.showerror("Error", f"{TEACHER_ATTENDANCE} not found!")

    def open_dashboard(self):
        if os.path.exists(DASHBOARD):
            subprocess.Popen([sys.executable, DASHBOARD])
        else:
            messagebox.showerror("Error", f"{DASHBOARD} not found!")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
