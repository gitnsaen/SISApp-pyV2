from tkinter import messagebox
import mysql_handler as dh
from app import SISApp

if __name__ == "__main__":
    if not dh.college_db.connect():
        messagebox.showerror("Database Error", "Failed to connect to database. Please check your MySQL configuration.")
        exit(1)

    app = SISApp()
    try:
        app.mainloop()
    finally:
        dh.college_db.disconnect()
        dh.program_db.disconnect()
        dh.student_db.disconnect()
