import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime

# Create a connection to the SQLite database
conn = sqlite3.connect('assignments.db')
c = conn.cursor()

# Function to refresh the widget content
def refresh_widget():
    listbox_widget.delete(0, tk.END)
    for row in c.execute("SELECT * FROM assignments WHERE status != 'Completed'"):
        listbox_widget.insert(tk.END, f"[Assignment] {row[1]}: {row[2]} (Due: {row[3]}, Status: {row[5]})")
    
    for row in c.execute("SELECT * FROM subtasks WHERE status != 'Completed'"):
        listbox_widget.insert(tk.END, f"[Subtask] {row[2]} (Due: {row[3]}, Status: {row[4]})")

    # Refresh every 60 seconds
    widget.after(60000, refresh_widget)

# Function to mark a task as "In Progress" or "Completed"
def mark_task(status):
    selected = listbox_widget.curselection()
    if selected:
        selected_text = listbox_widget.get(selected[0])
        if "[Assignment]" in selected_text:
            item_id = int(selected_text.split(':')[1].split()[0])
            c.execute("UPDATE assignments SET status = ? WHERE id = ?", (status, item_id))
        elif "[Subtask]" in selected_text:
            item_id = int(selected_text.split(':')[1].split()[0])
            c.execute("UPDATE subtasks SET status = ? WHERE id = ?", (status, item_id))
        
        conn.commit()
        refresh_widget()
    else:
        tkinter.messagebox.showwarning("Selection Error", "Please select an item to mark.")

# Function to close the widget
def close_widget():
    widget.destroy()

# Create the widget window
widget = tk.Tk()
widget.title("Assignment Widget")
widget.geometry("300x400+100+100")  # Position on desktop
widget.attributes('-topmost', True)  # Always on top
widget.overrideredirect(True)  # Frameless window

# Set transparency (semi-transparent window)
widget.attributes('-alpha', 0.9)

# Set window background to match desktop
widget.configure(bg='#2D2D2D')

frame_widget = tk.Frame(widget, bg='#2D2D2D')
frame_widget.pack(pady=10, padx=10, fill="both", expand=True)

listbox_widget = tk.Listbox(frame_widget, width=40, height=15, bg='#2D2D2D', fg='#FFFFFF', selectbackground='#3C3F41')
listbox_widget.pack(pady=5)

button_frame = tk.Frame(widget, bg='#2D2D2D')
button_frame.pack(pady=10, fill="x")

button_in_progress = tk.Button(button_frame, text="Mark as In Progress", bg='#3C3F41', fg='#FFFFFF', command=lambda: mark_task("In Progress"))
button_in_progress.pack(side="left", padx=10, pady=5)

button_completed = tk.Button(button_frame, text="Mark as Completed", bg='#3C3F41', fg='#FFFFFF', command=lambda: mark_task("Completed"))
button_completed.pack(side="right", padx=10, pady=5)

button_close = tk.Button(widget, text="Close Widget", bg='#3C3F41', fg='#FFFFFF', command=close_widget)
button_close.pack(pady=5)

# Initialize widget content
refresh_widget()

# Run the widget
widget.mainloop()
