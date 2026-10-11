import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error


# ---------- DATABASE CONNECTION ----------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="******",
        database="course_progress_db"
    )


# ---------- CREATE TABLE ----------
def create_table():
    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS course_progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                course_name VARCHAR(150) NOT NULL,
                progress INT NOT NULL,
                status VARCHAR(30) NOT NULL
            )
        """)
        con.commit()
        cur.close()
        con.close()
    except Error as e:
        messagebox.showerror("Database Error", str(e))
        root.destroy()


# ---------- CLEAR FIELDS ----------
def clear_fields():
    name_entry.delete(0, tk.END)
    course_entry.delete(0, tk.END)
    progress_entry.delete(0, tk.END)
    status_combo.set("In Progress")
    selected_id.set("")


# ---------- LOAD RECORDS ----------
def load_records():
    for item in table.get_children():
        table.delete(item)

    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("""
            SELECT id, student_name, course_name, progress, status
            FROM course_progress ORDER BY id DESC
        """)
        for row in cur.fetchall():
            table.insert("", tk.END, values=row)
        cur.close()
        con.close()
    except Error as e:
        messagebox.showerror("Database Error", str(e))


# ---------- SELECT RECORD ----------
def select_record(event):
    selected = table.focus()
    if not selected:
        return

    values = table.item(selected, "values")
    if values:
        clear_fields()
        selected_id.set(values[0])
        name_entry.insert(0, values[1])
        course_entry.insert(0, values[2])
        progress_entry.insert(0, values[3])
        status_combo.set(values[4])


# ---------- ADD RECORD ----------
def add_record():
    name = name_entry.get().strip()
    course = course_entry.get().strip()
    progress = progress_entry.get().strip()
    status = status_combo.get()

    if not name or not course or not progress:
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all fields."
        )
        return

    try:
        progress = int(progress)
        if not 0 <= progress <= 100:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Invalid Progress",
            "Progress must be a whole number from 0 to 100."
        )
        return

    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO course_progress
            (student_name, course_name, progress, status)
            VALUES (%s, %s, %s, %s)
        """, (name, course, progress, status))
        con.commit()
        cur.close()
        con.close()

        load_records()
        clear_fields()
        messagebox.showinfo("Success", "Record added successfully!")
    except Error as e:
        messagebox.showerror("Database Error", str(e))


# ---------- UPDATE RECORD ----------
def update_record():
    record_id = selected_id.get()
    if not record_id:
        messagebox.showwarning(
            "Select Record", "Select a record from the table first."
        )
        return

    name = name_entry.get().strip()
    course = course_entry.get().strip()
    progress = progress_entry.get().strip()
    status = status_combo.get()

    if not name or not course or not progress:
        messagebox.showwarning(
            "Missing Information", "Please fill in all fields."
        )
        return

    try:
        progress = int(progress)
        if not 0 <= progress <= 100:
            raise ValueError
    except ValueError:
        messagebox.showwarning(
            "Invalid Progress",
            "Progress must be a whole number from 0 to 100."
        )
        return

    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute("""
            UPDATE course_progress
            SET student_name=%s, course_name=%s,
                progress=%s, status=%s
            WHERE id=%s
        """, (name, course, progress, status, record_id))
        con.commit()
        cur.close()
        con.close()

        load_records()
        clear_fields()
        messagebox.showinfo("Success", "Record updated successfully!")
    except Error as e:
        messagebox.showerror("Database Error", str(e))


# ---------- DELETE RECORD ----------
def delete_record():
    record_id = selected_id.get()
    if not record_id:
        messagebox.showwarning(
            "Select Record", "Select a record from the table first."
        )
        return

    if not messagebox.askyesno(
        "Confirm Delete", "Are you sure you want to delete this record?"
    ):
        return

    try:
        con = connect_db()
        cur = con.cursor()
        cur.execute(
            "DELETE FROM course_progress WHERE id=%s",
            (record_id,)
        )
        con.commit()
        cur.close()
        con.close()

        load_records()
        clear_fields()
        messagebox.showinfo("Success", "Record deleted successfully!")
    except Error as e:
        messagebox.showerror("Database Error", str(e))


# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("Online Course Progress Management System")
root.geometry("1050x650")
root.configure(bg="#edf2f7")

selected_id = tk.StringVar()

title = tk.Label(
    root,
    text="ONLINE COURSE PROGRESS MANAGEMENT SYSTEM",
    font=("Arial", 19, "bold"),
    bg="#243b55",
    fg="white",
    pady=18
)
title.pack(fill="x")

form = tk.Frame(root, bg="white", padx=20, pady=15)
form.pack(fill="x", padx=20, pady=15)

tk.Label(
    form, text="Student Name:", bg="white",
    font=("Arial", 11)
).grid(row=0, column=0, sticky="w", padx=8, pady=8)

name_entry = tk.Entry(form, font=("Arial", 11), width=25)
name_entry.grid(row=0, column=1, padx=8, pady=8)

tk.Label(
    form, text="Course Name:", bg="white",
    font=("Arial", 11)
).grid(row=0, column=2, sticky="w", padx=8, pady=8)

course_entry = tk.Entry(form, font=("Arial", 11), width=25)
course_entry.grid(row=0, column=3, padx=8, pady=8)

tk.Label(
    form, text="Progress (0-100%):", bg="white",
    font=("Arial", 11)
).grid(row=1, column=0, sticky="w", padx=8, pady=8)

progress_entry = tk.Entry(form, font=("Arial", 11), width=25)
progress_entry.grid(row=1, column=1, padx=8, pady=8)

tk.Label(
    form, text="Course Status:", bg="white",
    font=("Arial", 11)
).grid(row=1, column=2, sticky="w", padx=8, pady=8)

status_combo = ttk.Combobox(
    form,
    values=["Not Started", "In Progress", "Completed"],
    state="readonly",
    width=23,
    font=("Arial", 11)
)
status_combo.grid(row=1, column=3, padx=8, pady=8)
status_combo.set("In Progress")

buttons = tk.Frame(root, bg="#edf2f7")
buttons.pack(pady=5)

tk.Button(
    buttons, text="Add Record", command=add_record,
    bg="#198754", fg="white", width=14
).grid(row=0, column=0, padx=6)

tk.Button(
    buttons, text="Update Record", command=update_record,
    bg="#0d6efd", fg="white", width=14
).grid(row=0, column=1, padx=6)

tk.Button(
    buttons, text="Delete Record", command=delete_record,
    bg="#dc3545", fg="white", width=14
).grid(row=0, column=2, padx=6)

tk.Button(
    buttons, text="Clear Fields", command=clear_fields,
    bg="#6c757d", fg="white", width=14
).grid(row=0, column=3, padx=6)

tk.Button(
    buttons, text="Refresh", command=load_records,
    bg="#6f42c1", fg="white", width=14
).grid(row=0, column=4, padx=6)

table_frame = tk.Frame(root, bg="white")
table_frame.pack(fill="both", expand=True, padx=20, pady=15)

columns = ("ID", "Student Name", "Course Name", "Progress", "Status")

table = ttk.Treeview(
    table_frame, columns=columns, show="headings", height=12
)

for col in columns:
    table.heading(col, text=col)
    table.column(col, width=180, anchor="center")

table.pack(fill="both", expand=True)
table.bind("<<TreeviewSelect>>", select_record)

create_table()

if root.winfo_exists():
    load_records()
    root.mainloop()