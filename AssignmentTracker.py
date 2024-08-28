import customtkinter as ctk
import tkinter.messagebox as messagebox
import sqlite3
from datetime import datetime

# Create a connection to the SQLite database
conn = sqlite3.connect('assignments.db')
c = conn.cursor()

# Function to refresh the assignments list
def refresh_assignments():
    textbox_assignments.delete("1.0", ctk.END)
    for row in c.execute("SELECT * FROM assignments WHERE status != 'Completed'"):
        textbox_assignments.insert(ctk.END, f"ID: {row[0]} | Module: {row[1]} | Title: {row[2]} | Due Date: {row[3]} | Status: {row[5]}\n")

# Function to refresh the subtasks list
def refresh_subtasks(assignment_id=None):
    textbox_subtasks.delete("1.0", ctk.END)
    query = "SELECT * FROM subtasks WHERE status != 'Completed'"
    params = ()
    if assignment_id:
        query += " AND assignment_id = ?"
        params = (assignment_id,)
    for row in c.execute(query, params):
        textbox_subtasks.insert(ctk.END, f"ID: {row[0]} | Title: {row[2]} | Due Date: {row[3]} | Status: {row[4]}\n")

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
    selected_assignment = textbox_assignments.tag_ranges(ctk.SEL)
    
    if selected_assignment:
        assignment_id = textbox_assignments.get(selected_assignment[0], selected_assignment[1]).split('|')[0].split(':')[1].strip()
        title = entry_subtask_title.get()
        due_date = entry_subtask_due_date.get()
        status = "Not Started"
        
        if title and due_date:
            c.execute("INSERT INTO subtasks (assignment_id, title, due_date, status) VALUES (?, ?, ?, ?)",
                      (assignment_id, title, due_date, status))
            conn.commit()
            messagebox.showinfo("Success", "Subtask added successfully!")
            refresh_subtasks(assignment_id)
        else:
            messagebox.showwarning("Input Error", "Please fill out all fields.")
    else:
        messagebox.showwarning("Selection Error", "Please select an assignment to add a subtask.")

# Function to mark a task or assignment as completed
def mark_as_completed():
    selected_assignment = textbox_assignments.tag_ranges(ctk.SEL)
    selected_subtask = textbox_subtasks.tag_ranges(ctk.SEL)
    
    if selected_assignment:
        assignment_id = textbox_assignments.get(selected_assignment[0], selected_assignment[1]).split('|')[0].split(':')[1].strip()
        c.execute("UPDATE assignments SET status = 'Completed' WHERE id = ?", (assignment_id,))
        conn.commit()
        refresh_assignments()
        refresh_subtasks()

    elif selected_subtask:
        subtask_id = textbox_subtasks.get(selected_subtask[0], selected_subtask[1]).split('|')[0].split(':')[1].strip()
        c.execute("UPDATE subtasks SET status = 'Completed' WHERE id = ?", (subtask_id,))
        conn.commit()
        refresh_subtasks()

    else:
        messagebox.showwarning("Selection Error", "Please select an assignment or subtask to mark as completed.")

# Function to set a task or assignment as in progress
def mark_as_in_progress():
    selected_assignment = textbox_assignments.tag_ranges(ctk.SEL)
    selected_subtask = textbox_subtasks.tag_ranges(ctk.SEL)
    
    if selected_assignment:
        assignment_id = textbox_assignments.get(selected_assignment[0], selected_assignment[1]).split('|')[0].split(':')[1].strip()
        c.execute("UPDATE assignments SET status = 'In Progress' WHERE id = ?", (assignment_id,))
        conn.commit()
        refresh_assignments()
        refresh_subtasks()

    elif selected_subtask:
        subtask_id = textbox_subtasks.get(selected_subtask[0], selected_subtask[1]).split('|')[0].split(':')[1].strip()
        c.execute("UPDATE subtasks SET status = 'In Progress' WHERE id = ?", (subtask_id,))
        conn.commit()
        refresh_subtasks()

    else:
        messagebox.showwarning("Selection Error", "Please select an assignment or subtask to mark as in progress.")

# Initialize the customtkinter application
app = ctk.CTk()
app.geometry("1000x600")
app.title("Assignment Tracker")

# Set the dark mode theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Create input fields for assignments
entry_module = ctk.CTkEntry(app, placeholder_text="Module Name")
entry_module.grid(row=0, column=0, padx=20, pady=10)

entry_title = ctk.CTkEntry(app, placeholder_text="Assignment Title")
entry_title.grid(row=1, column=0, padx=20, pady=10)

entry_due_date = ctk.CTkEntry(app, placeholder_text="Due Date (YYYY-MM-DD)")
entry_due_date.grid(row=2, column=0, padx=20, pady=10)

entry_description = ctk.CTkEntry(app, placeholder_text="Description")
entry_description.grid(row=3, column=0, padx=20, pady=10)

button_add_assignment = ctk.CTkButton(app, text="Add Assignment", command=add_assignment)
button_add_assignment.grid(row=4, column=0, padx=20, pady=10)

# Create input fields for subtasks
entry_subtask_title = ctk.CTkEntry(app, placeholder_text="Subtask Title")
entry_subtask_title.grid(row=5, column=0, padx=20, pady=10)

entry_subtask_due_date = ctk.CTkEntry(app, placeholder_text="Subtask Due Date (YYYY-MM-DD)")
entry_subtask_due_date.grid(row=6, column=0, padx=20, pady=10)

button_add_subtask = ctk.CTkButton(app, text="Add Subtask to Selected Assignment", command=add_subtask)
button_add_subtask.grid(row=7, column=0, padx=20, pady=10)

# Create buttons for status management
button_mark_in_progress = ctk.CTkButton(app, text="Mark as In Progress", command=mark_as_in_progress)
button_mark_in_progress.grid(row=8, column=0, padx=20, pady=10)

button_mark_completed = ctk.CTkButton(app, text="Mark as Completed", command=mark_as_completed)
button_mark_completed.grid(row=9, column=0, padx=20, pady=10)

# Create text boxes for assignments and subtasks
textbox_assignments = ctk.CTkTextbox(app, width=500, height=300)
textbox_assignments.grid(row=0, column=1, rowspan=5, padx=20, pady=10)

textbox_subtasks = ctk.CTkTextbox(app, width=500, height=300)
textbox_subtasks.grid(row=5, column=1, rowspan=5, padx=20, pady=10)

# Initialize content
refresh_assignments()

# Run the application
app.mainloop()
