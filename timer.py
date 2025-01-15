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
            target_duration INTEGER,
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
    global timer_label, finish_button, timer_running
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Capture the start time
    remaining_time = duration * 60  # Convert minutes to seconds
    timer_running = True

    def countdown():
        nonlocal remaining_time
        while remaining_time > 0 and timer_running:
            mins, secs = divmod(remaining_time, 60)
            timer_label.config(text=f"Time Left: {mins:02}:{secs:02}")
            root.update()
            time.sleep(1)
            remaining_time -= 1

        if not timer_running:
            return #timer stopped early

        # Handle time up
        timer_label.config(text="Time's Up!", fg="red")
        messagebox.showinfo("Time's Up!", "Your timer has ended.")

    def finish_timer():
        nonlocal remaining_time
        timer_running = False
        elapsed_time = duration * 60 - remaining_time
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        messagebox.showinfo("Timer Finished", "Task finished early!")
        timer_label.config(text=f"Finished! Elapsed: {elapsed_time // 60} min {elapsed_time % 60} sec")
        save_record(task_note, start_time, end_time, elapsed_time, duration, finished_early=True)
        finish_button.grid_remove()  # Hide the finish button

    # Create a new label for the timer
    timer_label = tk.Label(root, text=f"Time Left: {duration}:00", font=("Helvetica", 14))
    timer_label.grid(row=3, column=0, columnspan=2, pady=10)

       # Create the finish button
    finish_button = tk.Button(root, text="Finish Early", command=finish_timer)
    finish_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Start the countdown in a new thread
    threading.Thread(target=countdown).start()

def save_record(task_note, start_time, end_time, elapsed_time, target_duration, finished_early):
    """
    Save the task details to the SQLite database.
    
    Parameters:
        task_note (str): The note or description of the task.
        start_time (str): The timestamp when the task was started.
        end_time (str): The timestamp when the task was finished.
        elapsed_time (int): The elapsed time in seconds.
        finished_early (bool): True if the task was finished early, False if completed normally.
    """
    try:
        conn = sqlite3.connect("productivity_timer.db")
        cursor = conn.cursor()

        
        # Insert the record into the database
        cursor.execute('''
            INSERT INTO timer_records (task_note, start_time, end_time, duration, finished_early)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_note, start_time, end_time, elapsed_time, target_duration, finished_early))

        conn.commit()
        conn.close()
        print("Record saved successfully.")
    except Exception as e:
        print(f"Error saving record: {e}")


# Main execution
if __name__ == "__main__":
    initialize_database()
    create_ui()
