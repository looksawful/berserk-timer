import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import Optional
from .logger import view_today_log, delete_all_logs


def show_message(message: str, parent: Optional[tk.Tk] = None) -> None:
    messagebox.showinfo("Timer Finished", message, parent=parent)


def show_witness_form(parent: tk.Tk) -> Optional[str]:
    result: Optional[str] = None

    def submit() -> None:
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


ASCII_LOGO = r"""
███   ▄███▄   █▄▄▄▄   ▄▄▄▄▄   ▄███▄   █▄▄▄▄ █  █▀
█  █  █▀   ▀  █  ▄▀  █     ▀▄ █▀   ▀  █  ▄▀ █▄█
█ ▀ ▄ ██▄▄    █▀▀▌ ▄  ▀▀▀▀▄   ██▄▄    █▀▀▌  █▀▄
█  ▄▀ █▄   ▄▀ █  █  ▀▄▄▄▄▀    █▄   ▄▀ █  █  █  █
███   ▀███▀      █             ▀███▀     █     █
                ▀                       ▀     ▀
"""


def run_gui_timer(timer, witness_mode: bool, custom_phrase: Optional[str], config: dict) -> tk.Tk:
    root = tk.Tk()
    root.title("Berserk Timer")
    logo_label = tk.Label(root, text=ASCII_LOGO, font=(
        "Courier New", 10), justify="left")
    logo_label.grid(row=0, column=0, columnspan=4, pady=(20, 0))
    time_label = tk.Label(
        root, text=f"Time remaining: {timer.get_remaining_time_str()}", font=("Helvetica", 24))
    time_label.grid(row=0, column=0, columnspan=4, pady=4)

    def pause() -> None:
        timer.pause()

    def resume() -> None:
        timer.resume()

    def quit_timer() -> None:
        timer.stop()
        root.destroy()

    def zero() -> None:
        timer.zero()
        root.destroy()

    def restart() -> None:
        timer.restart()

    def view_log() -> None:
        log_content = view_today_log()
        messagebox.showinfo("Today's Log", log_content, parent=root)

    def delete_logs() -> None:
        delete_all_logs()
        messagebox.showinfo("Logs", "All logs deleted.", parent=root)

    def update_duration() -> None:
        new_duration = simpledialog.askfloat(
            "Update Duration", "Enter new duration in minutes:", parent=root)
        if new_duration is not None:
            timer.update_duration(new_duration * 60)

    def set_goal() -> None:
        new_goal = simpledialog.askstring(
            "Set Goal", "Enter your goal:", parent=root)
        if new_goal is not None:
            timer.set_goal(new_goal)

    button_frame = tk.Frame(root)
    button_frame.grid(row=1, column=0, columnspan=4, pady=10)
    tk.Button(button_frame, text="Pause", command=pause).grid(
        row=0, column=0, padx=5)
    tk.Button(button_frame, text="Resume", command=resume).grid(
        row=0, column=1, padx=5)
    tk.Button(button_frame, text="Quit", command=quit_timer).grid(
        row=0, column=2, padx=5)
    tk.Button(button_frame, text="Zero", command=zero).grid(
        row=0, column=3, padx=5)
    tk.Button(button_frame, text="Restart", command=restart).grid(
        row=1, column=0, padx=5, pady=5)
    tk.Button(button_frame, text="View Log", command=view_log).grid(
        row=1, column=1, padx=5, pady=5)
    tk.Button(button_frame, text="Delete Logs", command=delete_logs).grid(
        row=1, column=2, padx=5, pady=5)
    tk.Button(button_frame, text="Update Duration", command=update_duration).grid(
        row=2, column=0, padx=5, pady=5)
    tk.Button(button_frame, text="Set Goal", command=set_goal).grid(
        row=2, column=1, padx=5, pady=5)

    def update_label() -> None:
        try:
            if timer.get_remaining_time() <= 0:
                time_label.config(text="Time's up!")
                root.after(1000, root.destroy)
            else:
                time_label.config(
                    text=f"Time remaining: {timer.get_remaining_time_str()}")
                root.after(1000, update_label)
        except tk.TclError:
            pass
    update_label()
    root.mainloop()
    return root


def ask_restart_gui(root: tk.Tk) -> bool:
    return messagebox.askyesno("Restart Timer", "Do you want to restart the timer?", parent=root)
