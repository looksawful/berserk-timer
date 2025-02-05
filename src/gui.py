# The GUI is totaly experimental, you SHOULD NOT expect it to work fine.
# Yet NO witness-mode for gui, sorry.

import tkinter as tk
from tkinter import messagebox
from .logger import view_today_log, delete_all_logs


def show_message(message, parent=None):
    messagebox.showinfo("Timer Finished", message, parent=parent)

# TODO GUI witness-mode


def show_witness_form(parent):
    #     """Asks user to enter activity description in CLI after the timer ends.
    #     Input cannot be empty."""
    result = None

    def submit():
        nonlocal result
        if not entry.get().strip():
            messagebox.showerror(
                "Input Error", "Please enter what you were doing.", parent=parent)
            return
        result = entry.get().strip()
        form.destroy()

    form = tk.Toplevel(parent)
    form.title("Witness Mode")
    tk.Label(form, text="What were you doing?").pack(padx=20, pady=10)
    entry = tk.Entry(form, width=40)
    entry.pack(padx=20, pady=10)
    tk.Button(form, text="Submit", command=submit).pack(padx=20, pady=10)
    form.mainloop()
    return result


def run_gui_timer(timer, witness_mode, custom_phrase, config):
    root = tk.Tk()
    root.title("Berserk Timer")

    time_label = tk.Label(
        root, text=f"Time remaining: {timer.get_remaining_time_str()}", font=("Helvetica", 24))
    time_label.grid(pady=20)

    def pause():
        timer.pause()

    def resume():
        timer.resume()

    def quit_timer():
        timer.stop()
        root.destroy()

    def zero():
        timer.zero()
        root.destroy()

    def restart():
        timer.restart()

    def restart_timer():
        timer.restart()
        update_label()

    def view_log():
        log_content = view_today_log()
        messagebox.showinfo("Today's Log", log_content, parent=root)

    def delete_logs():
        delete_all_logs()
        messagebox.showinfo("Logs", "All logs deleted.", parent=root)

    button_frame = tk.Frame(root)
    button_frame.grid(pady=10)
    tk.Button(button_frame, text="Pause", command=pause).grid(
        row=0, column=0, padx=5)
    tk.Button(button_frame, text="Resume", command=resume).grid(
        row=0, column=1, padx=5)
    tk.Button(button_frame, text="Quit", command=quit_timer).grid(
        row=0, column=2, padx=5)
    tk.Button(button_frame, text="Zero", command=zero).grid(
        row=1, column=0, padx=5, pady=5)
    tk.Button(button_frame, text="Restart", command=restart).grid(
        row=1, column=1, padx=5, pady=5)
    tk.Button(button_frame, text="View Log", command=view_log).grid(
        row=1, column=3, padx=5, pady=5)
    tk.Button(button_frame, text="Delete Logs", command=delete_logs).grid(
        row=1, column=4, padx=5, pady=5)

    def update_label():
        try:
            if timer.get_remaining_time() <= 0:
                time_label.config(text="Time's up!")
                # Schedule destruction of the window after a short delay.
                root.after(1000, root.destroy)
            else:
                time_label.config(
                    text=f"Time remaining: {timer.get_remaining_time_str()}")
                # Reschedule the update_label callback.
                root.after(1000, update_label)
        except tk.TclError:
            # This exception is raised if the widget has been destroyed.
            pass

    update_label()
    root.mainloop()
    return root
