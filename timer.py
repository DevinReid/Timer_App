# 1. Import libraries
import tkinter as tk
from tkinter import messagebox
import time
import sqlite3


# Initialize the app
def initialize_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect("productivity_timer.db")
    cursor = conn.cursor()

    # Create a table for storing timer records if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timer_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_note TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER,
            finished_early BOOLEAN
        )
    ''')

    conn.commit()
    conn.close()

# Build the UI
def create_ui():
    # Create the main window
    root = tk.Tk()
    root.title("Productivity Timer")

    # Task note label and entry
    tk.Label(root, text="Task Note:").grid(row=0, column=0, padx=10, pady=10)
    task_note_var = tk.StringVar()
    task_entry = tk.Entry(root, textvariable=task_note_var, width=40)
    task_entry.grid(row=0, column=1, padx=10, pady=10)

    # Time selection label and dropdown
    tk.Label(root, text="Set Time (minutes):").grid(row=1, column=0, padx=10, pady=10)
    time_var = tk.IntVar(value=5)
    time_options = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
    time_menu = tk.OptionMenu(root, time_var, *time_options)
    time_menu.grid(row=1, column=1, padx=10, pady=10)

    # Start button (disabled initially)
    def enable_start_button(*args):
        start_button.config(state="normal" if task_note_var.get() else "disabled")

    task_note_var.trace("w", enable_start_button)

    start_button = tk.Button(root, text="Start Timer", state="disabled", command=lambda: start_timer(time_var.get(), task_note_var.get()))
    start_button.grid(row=2, column=0, columnspan=2, pady=20)

    # Run the main loop
    root.mainloop()

# Placeholder for the start_timer function
def start_timer(duration, task_note):
    messagebox.showinfo("Timer Started", f"Task: {task_note}\nDuration: {duration} minutes")
    # Timer logic will be implemented later

# Main execution
if __name__ == "__main__":
    initialize_database()
    create_ui()
