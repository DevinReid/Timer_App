# 1. Import libraries
import tkinter as tk
from tkinter import messagebox
import time
import sqlite3
import threading


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

    start_button = tk.Button(root, text="Start Timer", state="disabled", command=lambda: start_timer(time_var.get(), task_note_var.get(), root))
    start_button.grid(row=2, column=0, columnspan=2, pady=20)

    # Run the main loop
    root.mainloop()

# Placeholder for the start_timer function
# Start the timer and show countdown
# Start the timer and show countdown
def start_timer(duration, task_note, root):
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Capture the start time
    remaining_time = duration * 60  # Convert minutes to seconds

    def countdown():
        nonlocal remaining_time
        while remaining_time > 0:
            mins, secs = divmod(remaining_time, 60)
            timer_label.config(text=f"Time Left: {mins:02}:{secs:02}")
            root.update()
            time.sleep(1)
            remaining_time -= 1

        # Handle time up
        timer_label.config(text="Time's Up!", fg="red")
        messagebox.showinfo("Time's Up!", "Your timer has ended.")

    # Create a new label for the timer
    timer_label = tk.Label(root, text=f"Time Left: {duration}:00", font=("Helvetica", 14))
    timer_label.grid(row=3, column=0, columnspan=2, pady=10)

    # Start the countdown in a new thread
    threading.Thread(target=countdown).start()



# Main execution
if __name__ == "__main__":
    initialize_database()
    create_ui()
