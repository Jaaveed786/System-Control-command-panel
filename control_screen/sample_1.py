import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import platform
import psutil
import screen_brightness_control as sbc
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from time import strftime
import tkcalendar
from tkcalendar import *
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import pyautogui
import subprocess
import webbrowser as wb
import random

# Initialize Tkinter Window
root = Tk()
root.title('Windows Tool')
root.geometry("850x500+300+170")
root.resizable(False, False)
root.configure(bg="#292e2e")

# Brightness Control
def set_brightness(value):
    sbc.set_brightness(int(value))

ttk.Label(root, text="Brightness:", background="#292e2e", foreground="white").place(x=30, y=20)
brightness_slider = ttk.Scale(root, from_=0, to=100, orient=HORIZONTAL, command=set_brightness)
brightness_slider.set(sbc.get_brightness()[0])
brightness_slider.place(x=120, y=20)

# Volume Control
def set_volume(value):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(float(value) / 100, None)

ttk.Label(root, text="Volume:", background="#292e2e", foreground="white").place(x=30, y=60)
volume_slider = ttk.Scale(root, from_=0, to=100, orient=HORIZONTAL, command=set_volume)
volume_slider.set(50)
volume_slider.place(x=120, y=60)

# System Info
def system_info():
    info = f"System: {platform.system()}\nVersion: {platform.version()}\nProcessor: {platform.processor()}\nRAM: {psutil.virtual_memory().total // (1024**3)} GB"
    messagebox.showinfo("System Info", info)

ttk.Button(root, text="System Info", command=system_info).place(x=30, y=100)

# Date & Time
def show_time():
    time_label.config(text=strftime('%H:%M:%S'))
    root.after(1000, show_time)

time_label = Label(root, font=('calibri', 12), background='#292e2e', foreground='white')
time_label.place(x=30, y=150)
show_time()

# Weather Functionality
def get_weather():
    city = "London"  # You can modify this to get user input
    api_key = "your_api_key"  # Replace with your OpenWeatherMap API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    weather_info = f"{city}\nTemp: {response['main']['temp']}°C\nWeather: {response['weather'][0]['description']}"
    messagebox.showinfo("Weather Info", weather_info)

ttk.Button(root, text="Weather", command=get_weather).place(x=30, y=200)

# Screenshot Function
def take_screenshot():
    screenshot = pyautogui.screenshot()
    filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if filepath:
        screenshot.save(filepath)
        messagebox.showinfo("Success", "Screenshot saved successfully!")

ttk.Button(root, text="Screenshot", command=take_screenshot).place(x=30, y=250)

# Open Browser
def open_browser():
    wb.open("https://www.google.com")

ttk.Button(root, text="Open Browser", command=open_browser).place(x=30, y=300)

# Open Calculator
def open_calculator():
    subprocess.run("calc")

ttk.Button(root, text="Calculator", command=open_calculator).place(x=30, y=350)

# Mainloop
root.mainloop()
