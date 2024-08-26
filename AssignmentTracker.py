import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from plyer import notification
from datetime import datetime, timedelta

# Create a connection to the SQLite database
conn = sqlite3.connect('assignments.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS assignments
             (id INTEGER PRIMARY KEY, module TEXT, title TEXT, due_date TEXT, description TEXT, status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS subtasks
             (id INTEGER PRIMARY KEY, assignment_id INTEGER, title TEXT, due_date TEXT, status TEXT,
             FOREIGN KEY(assignment_id) REFERENCES assignments(id))''')
conn.commit()

# Function to add an assignment
def add_assignment():
    module = entry_module.get()
    title = entry_title.get()
    due_date = entry_due_date.get()
    description = entry_description.get()
    status = "Not Started"
    
    if module and title and due_date:
        c.execute("INSERT INTO assignments (module, title, due_date, description, status) VALUES (?, ?, ?, ?, ?)",
                  (module, title, due_date, description, status))
        conn.commit()
        messagebox.showinfo("Success", "Assignment added successfully!")
        refresh_assignments()
    else:
        messagebox.showwarning("Input Error", "Please fill out all fields.")

# Function to add a subtask
def add_subtask():
    selected = listbox_assignments.curselection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select an assignment to add a subtask.")
        return
    
    assignment_id = listbox_assignments.get(selected[0]).split('|')[0].split(':')[1].strip()
    title = simpledialog.askstring("Subtask Title", "Enter the subtask title:")
    due_date = simpledialog.askstring("Subtask Due Date", "Enter the subtask due date (YYYY-MM-DD):")
    
    if title and due_date:
        c.execute("INSERT INTO subtasks (assignment_id, title, due_date, status) VALUES (?, ?, ?, ?)",
                  (assignment_id, title, due_date, "Not Started"))
        conn.commit()
        messagebox.showinfo("Success", "Subtask added successfully!")
        refresh_subtasks(assignment_id)
    else:
        messagebox.showwarning("Input Error", "Please fill out all fields.")

# Function to refresh the assignments list
def refresh_assignments():
    listbox_assignments.delete(0, tk.END)
    for row in c.execute("SELECT * FROM assignments"):
        listbox_assignments.insert(tk.END, f"ID: {row[0]} | Module: {row[1]} | Title: {row[2]} | Due Date: {row[3]} | Status: {row[5]}")

# Function to refresh the subtasks list
def refresh_subtasks(assignment_id):
    listbox_subtasks.delete(0, tk.END)
    for row in c.execute("SELECT * FROM subtasks WHERE assignment_id = ?", (assignment_id,)):
        listbox_subtasks.insert(tk.END, f"ID: {row[0]} | Title: {row[2]} | Due Date: {row[3]} | Status: {row[4]}")

# Function to mark a task or assignment as completed
def mark_as_completed(item_id, item_type):
    if item_type == 'assignment':
        c.execute("UPDATE assignments SET status = 'Completed' WHERE id = ?", (item_id,))
    elif item_type == 'subtask':
        c.execute("UPDATE subtasks SET status = 'Completed' WHERE id = ?", (item_id,))
    conn.commit()
    refresh_assignments()
    refresh_subtasks(item_id if item_type == 'assignment' else None)
    messagebox.showinfo("Task Completed", "The task has been marked as completed.")

# Function to send desktop notifications with snooze and done options
def send_desktop_notification(title, message, item_id, item_type):
    def snooze():
        root.after(60000, lambda: trigger_notification(item_id, item_type))

    def done():
        mark_as_completed(item_id, item_type)
    
    notification.notify(
        title=title,
        message=message,
        app_name='Assignment Tracker',
        timeout=10  # Duration of the notification in seconds
    )

    # Creating a temporary window to simulate snooze and done options
    temp_window = tk.Toplevel(root)
    temp_window.title("Notification")

    lbl = tk.Label(temp_window, text=message)
    lbl.pack(pady=10)

    btn_snooze = tk.Button(temp_window, text="Snooze", command=lambda: [snooze(), temp_window.destroy()])
    btn_snooze.pack(side=tk.LEFT, padx=10)

    btn_done = tk.Button(temp_window, text="Done", command=lambda: [done(), temp_window.destroy()])
    btn_done.pack(side=tk.RIGHT, padx=10)

# Function to trigger a notification
def trigger_notification(item_id, item_type):
    today = datetime.now()
    if item_type == 'assignment':
        row = c.execute("SELECT * FROM assignments WHERE id = ?", (item_id,)).fetchone()
        if row and row[5] != 'Completed':
            due_date = datetime.strptime(row[3], "%Y-%m-%d")
            if due_date <= today + timedelta(days=1):
                title = f"Reminder: {row[2]} is due soon!"
                message = f"Assignment '{row[2]}' in module '{row[1]}' is due on {row[3]}. Please make sure to complete it on time."
                send_desktop_notification(title, message, item_id, 'assignment')
    elif item_type == 'subtask':
        row = c.execute("SELECT * FROM subtasks WHERE id = ?", (item_id,)).fetchone()
        if row and row[4] != 'Completed':
            due_date = datetime.strptime(row[3], "%Y-%m-%d")
            if due_date <= today + timedelta(days=1):
                title = f"Reminder: Subtask '{row[2]}' is due soon!"
                message = f"Subtask '{row[2]}' is due on {row[3]}. Please make sure to complete it on time."
                send_desktop_notification(title, message, item_id, 'subtask')

# Function to check for due assignments and send reminders
def check_for_due_assignments():
    today = datetime.now()
    print(f"Checking for due assignments... Current time: {today}")
    for row in c.execute("SELECT * FROM assignments WHERE status = 'Not Started'"):
        due_date = datetime.strptime(row[3], "%Y-%m-%d")
        print(f"Checking assignment: {row[2]}, Due Date: {due_date}")
        if due_date <= today + timedelta(days=1):
            trigger_notification(row[0], 'assignment')

    for row in c.execute("SELECT * FROM subtasks WHERE status = 'Not Started'"):
        due_date = datetime.strptime(row[3], "%Y-%m-%d")
        print(f"Checking subtask: {row[2]}, Due Date: {due_date}")
        if due_date <= today + timedelta(days=1):
            trigger_notification(row[0], 'subtask')

    # Schedule the next check
    root.after(10000, check_for_due_assignments)  # Check every 10 seconds for testing

# GUI Setup
root = tk.Tk()
root.title("Assignment Tracker")

frame = tk.Frame(root)
frame.pack(pady=20)

label_module = tk.Label(frame, text="Module:")
label_module.grid(row=0, column=0)

entry_module = tk.Entry(frame)
entry_module.grid(row=0, column=1)

label_title = tk.Label(frame, text="Assignment Title:")
label_title.grid(row=1, column=0)

entry_title = tk.Entry(frame)
entry_title.grid(row=1, column=1)

label_due_date = tk.Label(frame, text="Assignment Due Date (YYYY-MM-DD):")
label_due_date.grid(row=2, column=0)

entry_due_date = tk.Entry(frame)
entry_due_date.grid(row=2, column=1)

label_description = tk.Label(frame, text="Description:")
label_description.grid(row=3, column=0)

entry_description = tk.Entry(frame)
entry_description.grid(row=3, column=1)

button_add_assignment = tk.Button(frame, text="Add Assignment", command=add_assignment)
button_add_assignment.grid(row=4, columnspan=2)

button_add_subtask = tk.Button(root, text="Add Subtask", command=add_subtask)
button_add_subtask.pack(pady=5)

listbox_assignments = tk.Listbox(root, width=50)
listbox_assignments.pack(pady=5)

listbox_subtasks = tk.Listbox(root, width=50)
listbox_subtasks.pack(pady=5)

refresh_assignments()

# Check for due assignments every 10 seconds for testing
root.after(10000, check_for_due_assignments)

root.mainloop()
