import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime
import heapq
import json
import os
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "tasks.json"
tasks = []

def save_tasks():
    data = []
    for t in tasks:
        score, name, deadline, priority = t
        data.append({
            "name": name,
            "deadline": deadline.strftime("%Y-%m-%d %H:%M"),
            "priority": priority
        })
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        for item in data:
            deadline = datetime.strptime(item["deadline"], "%Y-%m-%d %H:%M")
            now = datetime.now()
            time_left = (deadline - now).total_seconds()

            urgency = 1 / (time_left + 1)
            importance = (4 - item["priority"])
            score = (0.6 * urgency) + (0.4 * importance)

            heapq.heappush(tasks, (-score, item["name"], deadline, item["priority"]))

app = ctk.CTk()
app.title("Smart Task Scheduler (Advanced DAA)")
app.geometry("800x700")
app.configure(fg_color="#0f172a")


ctk.CTkLabel(app, text="🚀 Smart Task Scheduler (Advanced)",
             font=("Arial", 22, "bold")).pack(pady=10)


best_label = ctk.CTkLabel(app, text="", fg_color="#22c55e",
                         text_color="black", corner_radius=10,
                         font=("Arial", 14))
best_label.pack(fill="x", padx=20, pady=5)


frame = ctk.CTkFrame(app, corner_radius=12)
frame.pack(fill="x", padx=20, pady=10)

task_entry = ctk.CTkEntry(frame, placeholder_text="Enter Task")
task_entry.pack(padx=10, pady=5, fill="x")


date_entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
date_entry.pack(pady=5)


time_entry = ctk.CTkEntry(frame, placeholder_text="HH:MM (24hr)")
time_entry.pack(pady=5)


priority_menu = ctk.CTkOptionMenu(frame,
                                 values=["1 (High)", "2 (Medium)", "3 (Low)"])
priority_menu.set("1 (High)")
priority_menu.pack(pady=5)


search_entry = ctk.CTkEntry(app, placeholder_text="🔍 Search Task")
search_entry.pack(padx=20, pady=5, fill="x")


task_frame = ctk.CTkScrollableFrame(app)
task_frame.pack(fill="both", expand=True, padx=20, pady=10)


def add_task():
    name = task_entry.get()
    date = date_entry.get()
    time_str = time_entry.get()
    priority = int(priority_menu.get()[0])

    if not name or not time_str:
        best_label.configure(text="⚠ Please fill all fields")
        return

    try:
        deadline = datetime.strptime(date + " " + time_str, "%Y-%m-%d %H:%M")
    except:
        best_label.configure(text="⚠ Invalid time format")
        return

    now = datetime.now()
    time_left = (deadline - now).total_seconds()

    urgency = 1 / (time_left + 1)
    importance = (4 - priority)
    score = (0.6 * urgency) + (0.4 * importance)

    heapq.heappush(tasks, (-score, name, deadline, priority))

    save_tasks()

    task_entry.delete(0, "end")
    time_entry.delete(0, "end")

    render_tasks()


def delete_task(item):
    tasks.remove(item)
    heapq.heapify(tasks)
    save_tasks()
    render_tasks()
def edit_task(item):
    _, name, deadline, priority = item
    task_entry.delete(0, "end")
    task_entry.insert(0, name)
    time_entry.delete(0, "end")
    time_entry.insert(0, deadline.strftime("%H:%M"))
    priority_menu.set(f"{priority} ({'High' if priority==1 else 'Medium' if priority==2 else 'Low'})")
    delete_task(item)
def render_tasks():
    for widget in task_frame.winfo_children():
        widget.destroy()
    if not tasks:
        best_label.configure(text="")
        return
    keyword = search_entry.get().lower()
    sorted_tasks = sorted(tasks)
    best_label.configure(text=f"🔥 Do this first: {sorted_tasks[0][1]}")
    for t in sorted_tasks:
        score, name, deadline, priority = t
        if keyword and keyword not in name.lower():
            continue
        color = "#ef4444" if priority == 1 else "#f59e0b" if priority == 2 else "#10b981"
        card = ctk.CTkFrame(task_frame, corner_radius=15, fg_color="#1e293b")
        card.pack(fill="x", pady=10, padx=5)
        strip = ctk.CTkFrame(card, width=8, fg_color=color)
        strip.pack(side="left", fill="y")
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(content, text=name,
                     font=("Arial", 15, "bold")).pack(anchor="w")
        ctk.CTkLabel(content,
                     text=f"⏰ {deadline.strftime('%d %b %Y, %I:%M %p')}",
                     text_color="lightgray").pack(anchor="w", pady=2)
        ctk.CTkLabel(content,
                     text=f"⚡ Score: {round(-score,5)}",
                     text_color=color).pack(anchor="w")
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        edit_btn = ctk.CTkButton(btn_frame, text="✏️", width=40,
                                command=lambda x=t: edit_task(x))
        edit_btn.pack(side="left", padx=2)
        delete_btn = ctk.CTkButton(btn_frame, text="❌", width=40,
                                  fg_color="transparent",
                                  hover_color="#ef4444",
                                  command=lambda x=t: delete_task(x))
        delete_btn.pack(side="left", padx=2)

search_entry.bind("<KeyRelease>", lambda e: render_tasks())

ctk.CTkButton(app, text="Add Task", command=add_task).pack(pady=5)

load_tasks()
render_tasks()
app.mainloop()