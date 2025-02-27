import tkinter as tk
from tkinter import messagebox
import time
import sqlite3
import threading
from PIL import Image, ImageTk



class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity Timer")
        self.root.geometry("600x300")
        

        # Initialize variables
        self.timer_running = False
        self.pause_flag = False
        self.remaining_time = 0
        self.session_elasped_time = 0
        self.total_elapsed_time = 0
        self.start_time = None
        self.end_time = None
        self.task_note = None

        # Set up the database
        self.initialize_database()

        # Load background image
       
        self.background_image = Image.open("Timer_Background1.png").resize((600, 300))
        self.bg_photo = ImageTk.PhotoImage(self.background_image)
        
        self.bg_color = "#d747b3"
        
        print(f"Extracted background color: {self.bg_color}")
        # Create UI elements
        self.create_ui()

    def initialize_database(self):
        conn = sqlite3.connect("productivity_timer.db")
        cursor = conn.cursor()
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


    def create_ui(self):
        # Set root background to match the image border
        self.root.configure(bg="black")  # Match this to the outermost color of your image

        # Create a canvas to fill the entire root window
        canvas = tk.Canvas(self.root, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        # Add UI elements with precise positioning
        canvas.create_text(50, 40, anchor="nw", text="Task Note:", font=("Old School Adventures", 12), fill="white")
        self.task_note_var = tk.StringVar()
        self.task_entry = tk.Entry(self.root, textvariable=self.task_note_var, width=40)
        canvas.create_window(200, 40, anchor="nw", window=self.task_entry)

        canvas.create_text(60, 80, anchor="nw", text="Set Time (minutes):", font=("Old School Adventures", 12), fill="white")
        self.time_var = tk.IntVar(value=5)
        time_options = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        self.time_menu = tk.OptionMenu(self.root, self.time_var, *time_options)
        canvas.create_window(300, 80, anchor="nw", window=self.time_menu)

        # Start button
        self.start_button = tk.Button(self.root, text="Start Timer", state="disabled", font= ("Mx437 IBM MDA",12), command=self.start_timer)
        canvas.create_window(250, 130, anchor="nw", window=self.start_button)

        # Timer label
        self.timer_label = tk.Label(self.root, text="Time Left: 0:00", font=("Old School Adventures", 14), fg="black", bg=self.bg_color)
        canvas.create_window(300, 190, anchor="center", window=self.timer_label)

        # Pause/Resume button
        self.pause_resume_button = tk.Button(self.root, text="Pause", state="disabled", command=self.toggle_pause_resume)
        canvas.create_window(100, 230, anchor="nw", window=self.pause_resume_button)

        # Finish button
        self.finish_button = tk.Button(self.root, text="Finish Early", state="disabled", command=self.finish_timer)
        canvas.create_window(300, 240, anchor="center", window=self.finish_button)

        self.task_note_var.trace_add("write", self.enable_start_button)


    def enable_start_button(self, *args):
        self.start_button.config(state="normal" if self.task_note_var.get() else "disabled")

    def start_timer(self):
        self.task_note = self.task_note_var.get()
        self.remaining_time = self.time_var.get() * 60
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.timer_running = True
        self.pause_flag = False
        self.total_elapsed_time = 0
        # Disable buttons during countdown
        self.start_button.config(state="disabled")
        self.pause_resume_button.config(state="normal")
        self.finish_button.config(state="normal")

        # Start the countdown in a new thread
        threading.Thread(target=self.update_timer).start()

    def update_timer(self):
        while self.remaining_time > 0 and self.timer_running:
            if not self.pause_flag:
                mins, secs = divmod(self.remaining_time, 60)
                self.timer_label.config(text=f"Time Left: {mins:02}:{secs:02}")
                self.remaining_time -= 1
                time.sleep(1)

        if self.timer_running:  # Timer ended naturally
            self.timer_label.config(text="Time's up!")
            self.timer_running = False
            self.show_times_up_popup()


    def toggle_pause_resume(self):
        self.pause_flag = not self.pause_flag
        self.pause_resume_button.config(text="Resume" if self.pause_flag else "Pause")

    def finish_timer(self):
            self.timer_running = False
            self.session_elapsed_time = self.time_var.get() * 60 - self.remaining_time
            self.total_elapsed_time += self.session_elapsed_time
            end_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.save_record(self.total_elapsed_time, finished_early=True)
            self.timer_label.config(text=f"Finished early! Elapsed: {self.total_elapsed_time // 60} min {self.total_elapsed_time % 60} sec")
            self.start_button.config(state="normal")
            self.pause_resume_button.config(state="disabled")
            self.finish_button.config(state="disabled")


    def save_record(self, elapsed_time, finished_early):
            print("record saved")
            conn = sqlite3.connect("productivity_timer.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO timer_records (task_note, start_time, end_time, duration, target_duration, finished_early)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.task_note,
                self.start_time,
                time.strftime("%Y-%m-%d %H:%M:%S"),
                elapsed_time,
                self.time_var.get(),
                finished_early
            ))
            conn.commit()
            conn.close()

    def show_times_up_popup(self):
        # Stop the timer and calculate elapsed time
        self.timer_running = False
        self.session_elapsed_time = self.time_var.get() * 60 - self.remaining_time
        
        # Create the popup window
        popup = tk.Toplevel(self.root)
        popup.title("Time's Up!")
        popup.geometry("300x200")

        # Popup label
        tk.Label(popup, text="Time's up! Do you want to keep recording?").pack(pady=10)

        # Dropdown to select extra time
        tk.Label(popup, text="Extend by (minutes):").pack()
        extend_time_var = tk.IntVar(value=5)  # Default value is 5 minutes
        extend_time_menu = tk.OptionMenu(popup, extend_time_var, 1, 5, 10, 15, 20)
        extend_time_menu.pack(pady=5)

        def handle_keep_recording():
            # Extend the timer by the selected value
            extra_time = extend_time_var.get() * 60  # Convert minutes to seconds
            self.remaining_time += extra_time
            self.timer_running = True
            self.total_elapsed_time += self.session_elapsed_time
            popup.destroy()  # Close the popup

            # Restart the timer in a new thread
            threading.Thread(target=self.update_timer).start()

        def handle_finish():
            # Finalize the session
            end_time = time.strftime("%Y-%m-%d %H:%M:%S")
            self.total_elapsed_time += self.session_elapsed_time
            self.save_record(self.total_elapsed_time, finished_early=False)
            popup.destroy()  # Close the popup

            # Reset UI
            self.start_button.config(state="normal")
            self.pause_resume_button.config(state="disabled")
            self.finish_button.config(state="disabled")
            self.timer_label.config(text=f"Finished! Elapsed: {self.total_elapsed_time // 60} min")

        # Buttons for user actions
        tk.Button(popup, text="Keep Recording", command=handle_keep_recording).pack(side="left", padx=10, pady=10)
        tk.Button(popup, text="End Timer", command=handle_finish).pack(side="right", padx=10, pady=10)

        # Configure the popup to be modal
        popup.transient(self.root)  # Make the popup a child of the main window
        popup.grab_set()  # Block interaction with the main window until popup is closed
        self.root.wait_window(popup)  # Wait for the popup to close


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
