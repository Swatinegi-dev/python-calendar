import json
from calendar import calendar
from tkinter import *
from tkinter import ttk
from plyer import notification, temperature, humidity
from tkcalendar import Calendar
from tkinter import simpledialog, messagebox
from datetime import datetime,timedelta
import time
import requests

from weather import get_weather


def change_color(panel, current_color, target_color,step=1):
    current_rgb=panel.winfo_rgb(current_color)
    target_rgb=panel.winfo_rgb(target_color)
    new_rgb=tuple(min(max(c + step * (t - c) // 255, 0),65535) for c,t in zip(current_rgb,target_rgb))
    new_color="#%02x%02x%02x" % (new_rgb[0] // 256, new_rgb[1] // 256, new_rgb[2] //256)
    panel.config(bg=new_color)
    if new_rgb !=target_rgb:
        panel.after(300,change_color,panel,new_color,target_color,step)

root = Tk()
root.title("Calendar")
root.geometry("800x600")

# Create the main frame for the layout
main_frame = Frame(root)
main_frame.pack(fill=BOTH, expand=True)

# Left panel frame for buttons
left_panel = Frame(main_frame, bg="navy")
left_panel.pack(side=LEFT, expand=True,fill=BOTH)
root.after(2000,change_color,left_panel,"black","black",10)
# Calendar frame for displaying the calendar
calendar_frame = Frame(main_frame)
calendar_frame.pack(side=RIGHT, fill=BOTH, expand=True)

# Event and task data storage (dictionaries to hold data)
events_file = 'events.json'
tasks_file = 'tasks.json'



def load_data(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        return {}



def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)



events = load_data(events_file)
tasks = load_data(tasks_file)



def update_calendar():
    cal.calevent_remove('all')
    for date, event_list in events.items():  # Ensure events is a dictionary
        for event in event_list:
            cal.calevent_create(datetime.strptime(date, "%Y-%m-%d"), event, 'event')
    for date, task_list in tasks.items():  # Ensure tasks is a dictionary
        for task in task_list:
            cal.calevent_create(datetime.strptime(date, "%Y-%m-%d"), task, 'task')



def handle_event():
    operation = event_action.get()
    event_name = event_name_entry.get()
    event_date = cal.get_date()

    if operation == "Add Event":
        if event_date in events:
            events[event_date].append(event_name)
        else:
            events[event_date] = [event_name]
        save_data(events_file, events)
        messagebox.showinfo("Success", f"Event '{event_name}' added for {event_date}.")

    elif operation == "Edit Event":
        if event_date in events and event_name in events[event_date]:
            new_name = simpledialog.askstring("Edit Event", "Enter the new event name:")
            events[event_date][events[event_date].index(event_name)] = new_name
            save_data(events_file, events)
            messagebox.showinfo("Success", f"Event on {event_date} edited to '{new_name}'.")
        else:
            messagebox.showerror("Error", "Event not found.")

    elif operation == "Delete Event":
        if event_date in events and event_name in events[event_date]:
            events[event_date].remove(event_name)
            if not events[event_date]:
                del events[event_date]
            save_data(events_file, events)
            messagebox.showinfo("Success", f"Event '{event_name}' deleted.")
        else:
            messagebox.showerror("Error", "Event not found.")

    update_calendar()

def check(task_time,task_title,root):
    current_time=datetime.now().strftime("%H:%M")
    print(f"Checking task:{task_title}at{task_time},Current time:{current_time}")
    if current_time==task_time:
        messagebox.showinfo("Task Remainder",f"It's time for{task_title}")
    else:
        root.after(10000,lambda:check(task_time,task_title,root))
def notify():
    title=task_title_entry.get()
    time=task_time_entry.get()
    try:
        datetime.strptime(time,"%H:%M")
        check(time,title,root)
    except ValueError:
        messagebox.showerror("Input Error","Time must be in HH:MM")




def weather(city):
    api_key=""
    base_url=f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response=requests.get(base_url)
        weather_data=response.json()
        if weather_data["cod"]!="404":
            main=weather_data['main']
            temperature=main['temp']
            humidity=main['humidity']
            weather_des=weather_data['weather'][0]['des']
            return f"Temperature:{temperature}C\nHumidity:{humidity}%\nDescription:{weather_des}"
        else:
            return "City not found"
    except Exception as e:
        return f"An error occurred: {e}"

def display_weather():
    city = "Delhi"
    weather_info=get_weather(city)
    messagebox.showinfo("Weather Forcast",weather_info)
# Function to handle task operations (Add, Edit, Delete)
def handle_task():
    operation = task_action.get()
    task_name = task_name_entry.get()
    task_date = cal.get_date()

    if operation == "Add Task":
        if task_date in tasks:
            tasks[task_date].append(task_name)
        else:
            tasks[task_date] = [task_name]
        save_data(tasks_file, tasks)
        messagebox.showinfo("Success", f"Task '{task_name}' added for {task_date}.")

    elif operation == "Edit Task":
        if task_date in tasks and task_name in tasks[task_date]:
            new_name = simpledialog.askstring("Edit Task", "Enter the new task name:")
            tasks[task_date][tasks[task_date].index(task_name)] = new_name
            save_data(tasks_file, tasks)
            messagebox.showinfo("Success", f"Task on {task_date} edited to '{new_name}'.")
        else:
            messagebox.showerror("Error", "Task not found.")

    elif operation == "Delete Task":
        if task_date in tasks and task_name in tasks[task_date]:
            tasks[task_date].remove(task_name)
            if not tasks[task_date]:
                del tasks[task_date]
            save_data(tasks_file, tasks)
            messagebox.showinfo("Success", f"Task '{task_name}' deleted.")
        else:
            messagebox.showerror("Error", "Task not found.")

    update_calendar()


# Calendar widget
cal = Calendar(calendar_frame, background="black",normalbackground="#454545", foreground="white",selectmode="day", date_pattern="yyyy-mm-dd",headersforeground="white",font=("Times New Roman",25))
cal.pack(pady=20, padx=20, fill=BOTH, expand=True)

# Dropdown for event actions (Add, Edit, Delete)
event_action = ttk.Combobox(left_panel,values=["Add Event", "Edit Event", "Delete Event"],font=("Arial",18))
event_action.set("Add Event")
event_action.pack(pady=30)

# Event Name Entry

event_name_entry = Entry(left_panel,font=("Arial",16))
event_name_entry.insert(0,"Event Name",)
event_name_entry.pack(pady=5)


event_button = Button(left_panel, text="Submit Event",background="black",fg="white", font=("Arial",17),command=handle_event)
event_button.pack(pady=20)


task_action = ttk.Combobox(left_panel, values=["Add Task", "Edit Task", "Delete Task"],font=("Arial",18))
task_action.set("Add Task")
task_action.pack(pady=30)



task_name_entry = Entry(left_panel,font=("Arial",16))
task_name_entry.insert(0,"Task name")
task_name_entry.pack(pady=10)

# Task Button
task_button = Button(left_panel, text="Submit Task" ,background="black",fg="white", font=("Arial",17),command=handle_task)
task_button.pack(pady=10)



wbutton=Button(left_panel,font=("Arial",17),text="Get Weather",bg="lightblue",command=display_weather)
wbutton.pack(pady=10)


task_title_entry=Entry(left_panel,font=("Arial",16))
task_title_entry.insert(0,"Enter task title")
task_title_entry.pack(pady=5)


task_time_entry=Entry(left_panel,font=("Arial",16))
task_time_entry.insert(0,"Enter task time")
task_time_entry.pack(pady=10)
sb=Button(left_panel,font=("Arial",16),text="Set Task Notification",background="black",fg="white",command=notify)
sb.pack(pady=5)
# Load events and tasks into the calendar at the start
update_calendar()

# Start the Tkinter main loop
root.mainloop()