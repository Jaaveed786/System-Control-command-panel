import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import platform
import psutil
import screen_brightness_control as sbc
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from time import strftime
from tkcalendar import Calendar
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import pyautogui
import subprocess
import webbrowser as wb
import random


class ScreenController:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Screen Controller")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.setup_audio()
        self.create_widgets()
        self.update_clock()
        self.update_system_info()

    def setup_audio(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

    def create_widgets(self):
        self.create_notebook()
        self.create_system_tab()
        self.create_brightness_tab()
        self.create_volume_tab()
        self.create_calendar_tab()
        self.create_weather_tab()
        self.create_screen_tab()

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def create_system_tab(self):
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="System Info")

        # System information labels
        ttk.Label(system_frame, text="OS Version:").grid(row=0, column=0, padx=10, pady=5)
        self.os_label = ttk.Label(system_frame, text=platform.platform())
        self.os_label.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(system_frame, text="Battery Percentage:").grid(row=1, column=0, padx=10, pady=5)
        self.battery_label = ttk.Label(system_frame, text="")
        self.battery_label.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(system_frame, text="CPU Usage:").grid(row=2, column=0, padx=10, pady=5)
        self.cpu_label = ttk.Label(system_frame, text="")
        self.cpu_label.grid(row=2, column=1, padx=10, pady=5)

        # Clock
        self.clock_label = ttk.Label(system_frame, font=('Helvetica', 24))
        self.clock_label.grid(row=3, column=0, columnspan=2, pady=20)

        # System controls
        ttk.Button(system_frame, text="Shutdown", command=lambda: subprocess.call(["shutdown", "/s"])).grid(row=4,
                                                                                                            column=0,
                                                                                                            pady=10)
        ttk.Button(system_frame, text="Restart", command=lambda: subprocess.call(["shutdown", "/r"])).grid(row=4,
                                                                                                           column=1,
                                                                                                           pady=10)

    def create_brightness_tab(self):
        brightness_frame = ttk.Frame(self.notebook)
        self.notebook.add(brightness_frame, text="Brightness")

        self.brightness = tk.IntVar(value=sbc.get_brightness()[0])
        ttk.Label(brightness_frame, text="Screen Brightness").pack(pady=10)
        ttk.Scale(brightness_frame, variable=self.brightness, from_=0, to=100,
                  command=lambda e: sbc.set_brightness(self.brightness.get())).pack(pady=10)

        ttk.Button(brightness_frame, text="Random Brightness",
                   command=self.set_random_brightness).pack(pady=10)

    def create_volume_tab(self):
        volume_frame = ttk.Frame(self.notebook)
        self.notebook.add(volume_frame, text="Volume Control")

        self.vol_level = tk.DoubleVar()
        ttk.Label(volume_frame, text="Master Volume").pack(pady=10)
        ttk.Scale(volume_frame, variable=self.vol_level, from_=0, to=1,
                  command=self.set_volume).pack(pady=10)
        self.vol_level.set(self.volume.GetMasterVolumeLevelScalar())

    def create_calendar_tab(self):
        calendar_frame = ttk.Frame(self.notebook)
        self.notebook.add(calendar_frame, text="Calendar")

        self.cal = Calendar(calendar_frame, selectmode='day',
                            year=datetime.now().year, month=datetime.now().month,
                            day=datetime.now().day)
        self.cal.pack(pady=20)

        ttk.Button(calendar_frame, text="Get Date",
                   command=lambda: messagebox.showinfo("Selected Date", self.cal.get_date())).pack()

    def create_weather_tab(self):
        weather_frame = ttk.Frame(self.notebook)
        self.notebook.add(weather_frame, text="Weather")

        ttk.Label(weather_frame, text="Enter City:").pack(pady=5)
        self.city_entry = ttk.Entry(weather_frame)
        self.city_entry.pack(pady=5)

        ttk.Button(weather_frame, text="Get Weather", command=self.get_weather).pack(pady=10)
        self.weather_label = ttk.Label(weather_frame, text="")
        self.weather_label.pack(pady=10)

    def create_screen_tab(self):
        screen_frame = ttk.Frame(self.notebook)
        self.notebook.add(screen_frame, text="Screen Control")

        ttk.Button(screen_frame, text="Take Screenshot",
                   command=self.take_screenshot).pack(pady=10)

        ttk.Button(screen_frame, text="Search Web",
                   command=self.search_web).pack(pady=10)

        self.search_entry = ttk.Entry(screen_frame)
        self.search_entry.pack(pady=10)

    def set_volume(self, value):
        self.volume.SetMasterVolumeLevelScalar(float(value), None)

    def set_random_brightness(self):
        random_brightness = random.randint(0, 100)
        self.brightness.set(random_brightness)
        sbc.set_brightness(random_brightness)

    def update_clock(self):
        current_time = strftime('%H:%M:%S %p')
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def update_system_info(self):
        # Update battery information
        battery = psutil.sensors_battery()
        self.battery_label.config(text=f"{battery.percent}%")

        # Update CPU usage
        cpu_usage = psutil.cpu_percent()
        self.cpu_label.config(text=f"{cpu_usage}%")

        self.root.after(2000, self.update_system_info)

    def get_weather(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return

        try:
            geolocator = Nominatim(user_agent="screen_controller")
            location = geolocator.geocode(city)

            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)

            timezone = pytz.timezone(timezone_str)
            local_time = datetime.now(timezone).strftime("%H:%M:%S")

            api_key = "YOUR_OPENWEATHER_API_KEY"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url)
            data = response.json()

            weather_info = (
                f"Temperature: {data['main']['temp']}°C\n"
                f"Weather: {data['weather'][0]['description']}\n"
                f"Humidity: {data['main']['humidity']}%\n"
                f"Local Time: {local_time}"
            )
            self.weather_label.config(text=weather_info)
        except Exception as e:
            messagebox.showerror("Error", f"Could not retrieve data: {str(e)}")

    def take_screenshot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            screenshot = pyautogui.screenshot()
            screenshot.save(file_path)
            messagebox.showinfo("Success", "Screenshot saved successfully")

    def search_web(self):
        query = self.search_entry.get()
        if query:
            wb.open(f"https://www.google.com/search?q={query}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenController(root)
    root.mainloop()