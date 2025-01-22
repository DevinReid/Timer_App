# 1. Import libraries
import tkinter as tk
from tkinter import messagebox
import time
import sqlite3 ##KYLE - Need this for the database
import threading
from PIL import Image, ImageTk


# Initialize the app
def initialize_database(): ## KYLE--
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect("productivity_timer.db") ##this will create the .db file
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
    ''') ## this is sql that creates a specific table within the db. you need ''' ''' to do sql in sqlite3.  the rest are the column titles and their data type.

    conn.commit()  ##what it sounds like, this pushes the changes to the .db file
    conn.close() # closes the connection, can and will be reopened again, see the save_record function


def create_ui():
    global start_button
    # Create the main window
    root = tk.Tk()
    root.title("Productivity Timer")
    root.geometry("600x300")


    # Task note label and entry
    tk.Label(root, text="Task Note:").grid(row=0, column=0, padx=10, pady=10)
    task_note_var = tk.StringVar()
    task_entry = tk.Entry(root, textvariable=task_note_var, width=40)
    task_entry.grid(row=0, column=1, padx=10, pady=10)

    # Time selection label and dropdown
    tk.Label(root, text="Set Time (minutes):").grid(row=1, column=0, padx=10, pady=10)
    time_var = tk.IntVar(value=5)
    time_options = [.01, 1, 2, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
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


def start_timer(duration, task_note, root):
    global timer_label, pause_resume_button, finish_button, timer_running, is_timer_active, pause_flag, start_button, total_duration, total_elapsed_time

    total_elapsed_time = 0
    total_duration = duration
    is_timer_active = False
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Capture the start time
    remaining_time = duration * 60  # Convert minutes to seconds
    timer_running = True
    pause_flag = False 


    if 'timer_label' in globals():
        timer_label.config(text=f"Time Left: {duration}:00", fg="black") 

    if is_timer_active:
        response = messagebox.askyesno("Restart Timer", "A timer is already active. Do you want to restart it?")
        if not response:
            return  # Exit if the user doesn't want to restart the timer

        # Reset current timer
        timer_running = False
        pause_flag = False
        is_timer_active = False

    start_button.config(text="Start Timer", state= "disabled")
    def countdown():
        
        nonlocal remaining_time
        global is_timer_active, timer_running, total_duration, total_elapsed_time
        while remaining_time > 0:                                        
            if not timer_running:  # Exit if the timer is stopped early
                return
            if not pause_flag:  # Only decrement if not paused
                mins, secs = divmod(remaining_time, 60)
                timer_label.config(text=f"Time Left: {mins:02}:{secs:02}", fg="black")
                root.update()
                time.sleep(1)
                remaining_time -= 1

        if timer_running:  # If the timer ends naturally
            def handle_keep_recording():
                # Extend the timer by the selected dropdown value
                nonlocal remaining_time
                global timer_running, is_timer_active, total_duration, total_elapsed_time
                extra_time = extend_time_var.get() * 60  # Convert minutes to seconds
                remaining_time += extra_time  # Add the extra time
                total_duration += extend_time_var.get()  # Update the total duration (in minutes)
                timer_running = True  # Allow the timer to continue
                is_timer_active = True
                total_elapsed_time += elapsed_time
                popup.destroy()  # Close the popup
                # Restart the countdown
                threading.Thread(target=countdown).start()

            def handle_finish():
                global timer_running, is_timer_active, total_elapsed_time, elapsed_time
                timer_running = False  # Stop the timer
                elapsed_time = duration * 60 - remaining_time
                total_elapsed_time += elapsed_time
                end_time = time.strftime("%Y-%m-%d %H:%M:%S")
                save_record(task_note, start_time, end_time, total_elapsed_time, duration, finished_early=False)
                popup.destroy()  # Close the popup
                start_button.config(text="Start Timer", state="normal")  # Reset the button
                is_timer_active = False
                timer_label.config(text=f"Finished! Elapsed: {total_elapsed_time // 60} min {total_elapsed_time % 60} sec") 
                finish_button.config(state="disabled")
                pause_resume_button.config(state="disabled")

            # Show the "Time's Up" popup with options
            popup = tk.Toplevel(root)
            popup.title("Time's Up!")
            tk.Label(popup, text="Time's up! Do you want to keep recording?").pack(pady=10)

            # Dropdown to select extra time
            tk.Label(popup, text="Extend by (minutes):").pack()
            extend_time_var = tk.IntVar(value=5)
            extend_time_menu = tk.OptionMenu(popup, extend_time_var,  1, 5, 10, 15, 20)
            extend_time_menu.pack(pady=5)

            # Buttons for user actions
            tk.Button(popup, text="Keep Recording", command=handle_keep_recording).pack(side="left", padx=10, pady=10)
            tk.Button(popup, text="End Timer", command=handle_finish).pack(side="right", padx=10, pady=10)

            # Wait for the user to make a choice
            popup.transient(root)
            popup.grab_set()
            root.wait_window(popup)

        is_timer_active = False
        start_button.config(text="Start Timer", state="normal")

    def toggle_pause_resume():
        global pause_flag
        pause_flag = not pause_flag  # Toggle the pause flag
        if pause_flag:
            pause_resume_button.config(text="Resume")
        else:
            pause_resume_button.config(text="Pause")

    def finish_timer():
        nonlocal remaining_time
        global is_timer_active, timer_running
        timer_running = False
        elapsed_time = duration * 60 - remaining_time
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        messagebox.showinfo("Timer Finished", "Task finished early!")
        timer_label.config(text=f"Finished! Elapsed: {total_elapsed_time // 60} min {total_elapsed_time % 60} sec")
        save_record(task_note, start_time, end_time, elapsed_time, duration, finished_early=True)
        pause_resume_button.grid_remove()
        finish_button.grid_remove()  # Hide the finish button
        is_timer_active = False
        start_button.config(text="Start Timer", state="normal")

    # Create a new label for the timer
    timer_label = tk.Label(root, text=f"Time Left: {duration}:00", font=("Helvetica", 14))
    timer_label.grid(row=3, column=0, columnspan=2, pady=10)

    pause_resume_button = tk.Button(root, text="Pause", command=toggle_pause_resume)
    pause_resume_button.grid(row=4, column=0, pady=10)

       # Create the finish button
    finish_button = tk.Button(root, text="Finish Early", command=finish_timer)
    finish_button.grid(row=4, column=0, columnspan=2, pady=10)

    # Start the countdown in a new thread
    threading.Thread(target=countdown).start()

def save_record(task_note, start_time, end_time, elapsed_time, target_duration, finished_early): ##KYLE--
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
        cursor = conn.cursor()  ##You always need to call a cursor to make changes, i probably could have made this a global, single variable at the top

        
        # Insert the record into the database
        cursor.execute('''
            INSERT INTO timer_records (
                       task_note,
                        start_time, 
                       end_time, 
                       duration, 
                       target_duration, 
                       finished_early) 

            VALUES (?, ?, ?, ?, ?, ?)
        ''', (task_note, start_time, end_time, elapsed_time, target_duration, finished_early)) ## INSERT INTO calls what table and columns im going to store the data in in what order, 
        ##VALUES confirms how many values will be used with ? as a placeholder, this is done for security reasons i dont fully understand, has to do with the SQL itself being more vulnerable than python
        ## finally my actual parameters in Save_record get passed into those value ? slots, replacing them.

        conn.commit() #push changes to .db and close the connection
        conn.close()# I Call this function whenever i want data saved
        print("Record saved successfully.")
    except Exception as e:
        print(f"Error saving record: {e}")


# Main execution
if __name__ == "__main__":
    initialize_database()
    create_ui()
