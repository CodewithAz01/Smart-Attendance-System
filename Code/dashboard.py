import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import pandas as pd
from datetime import datetime

ATTENDANCE_FILE = "attendance.csv"

class DashboardApp(tb.Window):
    def __init__(self):
        super().__init__(title="🌸 Teacher Attendance Dashboard", themename="cosmo")
        self.geometry("1000x600")  # Increased width for spacing
        
        footer = ttk.Label(self, text="Developed by Abdullah Zahid",
                           font=("Segoe UI", 10, "italic"),
                           foreground="#555555")
        footer.pack(side="bottom", anchor="e", padx=10, pady=5)

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", pady=15)
        self.clock_label = ttk.Label(header, text="", font=("Segoe UI", 16, "bold"), foreground="#ff6347")
        self.clock_label.pack(side="right", padx=20)
        ttk.Label(header, text="📋 Smart Attendance Dashboard", font=("Segoe UI", 20, "bold"), foreground="#2e8b57").pack(side="left", padx=20)

        # Summary section
        self.summary_label = ttk.Label(self, text="", font=("Segoe UI", 14, "bold"), foreground="#4682b4")
        self.summary_label.pack(pady=10)

        # Table
        cols = ["Name", "RFID", "Date", "In Time", "Out Time"]
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"), foreground="#4b0082")
        style.configure("Treeview", font=("Segoe UI", 12), rowheight=200)  # increased rowheight for spacing
        style.map('Treeview', background=[('selected', '#add8e6')])

        self.table = ttk.Treeview(self, columns=cols, show="headings", height=18)
        for c in cols:
            self.table.heading(c, text=c)
            # Increase width and add padding
            self.table.column(c, width=180, anchor="w", minwidth=100)

        self.table.pack(padx=30, pady=10, fill="both", expand=True)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.load_data, bootstyle="success-outline", width=15).pack(side="left", padx=15)
        ttk.Button(btn_frame, text="❌ Exit", command=self.destroy, bootstyle="danger-outline", width=15).pack(side="left", padx=15)

        self.update_clock()
        self.load_data()

    def load_data(self):
        try:
            df = pd.read_csv(ATTENDANCE_FILE)
            for i in self.table.get_children():
                self.table.delete(i)
            for _, row in df.iterrows():
                # Add extra spacing by padding strings
                self.table.insert("", "end", values=[
                    f" {row['Name']}", f" {row['RFID']}", f" {row['Date']}", f" {row['In Time']}", f" {row['Out Time']}"
                ])
            
            # Summary stats
            today = datetime.now().strftime("%m/%d/%Y")
            today_df = df[df["Date"] == today]
            present = len(today_df)
            self.summary_label.config(text=f"Today ({today}) → Total Present: {present} ✅")
        except Exception as e:
            self.summary_label.config(text=f"Error loading data: {e}", foreground="red")

    def update_clock(self):
        now = datetime.now().strftime("%b %d, %Y — %I:%M:%S %p")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()
