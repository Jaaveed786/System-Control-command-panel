import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import platform
import psutil
import screen_brightness_control as sbc
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from datetime import datetime
import requests
import pytz
import pyautogui
import subprocess
import webbrowser as wb
import random
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from PIL import Image, ImageTk
import json


class AdvancedScreenController:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus Control Panel")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Theme Management
        self.theme_mode = tk.StringVar(value="light")
        self.themes = {
            "light": {"bg": "#ffffff", "fg": "#2c3e50", "accent": "#3498db"},
            "dark": {"bg": "#2c3e50", "fg": "#ecf0f1", "accent": "#3498db"},
            "system": {"bg": "SystemButtonFace", "fg": "SystemWindowText", "accent": "SystemHighlight"}
        }

        # Style Configuration
        self.style = ttk.Style()
        self.configure_styles()
        self.create_theme_switcher()

        # Application Setup
        self.setup_audio()
        self.create_widgets()
        self.update_clock()
        self.update_system_info()
        self.setup_news()

    def configure_styles(self):
        theme = self.themes[self.theme_mode.get()]
        self.style.theme_use('clam')

        self.style.configure('.', font=('Segoe UI', 12), background=theme['bg'])
        self.style.configure('TNotebook', background=theme['bg'])
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 12, 'bold'), padding=[20, 5])
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('TButton', background=theme['accent'], foreground='white',
                             borderwidth=0, font=('Segoe UI', 12, 'bold'))
        self.style.map('TButton', background=[('active', theme['accent'])])

    def create_theme_switcher(self):
        self.theme_btn = tk.Canvas(self.root, width=40, height=40, bd=0, highlightthickness=0)
        self.theme_btn.place(relx=0.98, rely=0.02, anchor='ne')
        self.draw_theme_icon()
        self.theme_btn.bind('<Button-1>', self.show_theme_menu)

    def draw_theme_icon(self):
        theme = self.theme_mode.get()
        self.theme_btn.delete('all')
        bg = self.themes[theme]['bg']
        fg = self.themes[theme]['fg']
        self.theme_btn.create_oval(2, 2, 38, 38, fill=fg, outline=fg)
        self.theme_btn.create_oval(8, 8, 32, 32, fill=bg, outline=bg)

    def show_theme_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Light Theme", command=lambda: self.change_theme('light'))
        menu.add_command(label="Dark Theme", command=lambda: self.change_theme('dark'))
        menu.add_command(label="System Theme", command=lambda: self.change_theme('system'))
        menu.tk_popup(event.x_root, event.y_root)

    def change_theme(self, mode):
        self.theme_mode.set(mode)
        self.configure_styles()
        self.draw_theme_icon()
        self.update_all_widgets()

    def update_all_widgets(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab in widget.tabs():
                    widget.nametowidget(tab).configure(style='TFrame')

    def setup_audio(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def create_widgets(self):
        self.create_notebook()
        self.create_dashboard_tab()
        self.create_media_tab()
        self.create_network_tab()
        self.create_news_tab()

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def create_dashboard_tab(self):
        dash_frame = ttk.Frame(self.notebook)
        self.notebook.add(dash_frame, text="Dashboard")

        # System Info Cards
        info_frame = ttk.Frame(dash_frame)
        info_frame.pack(pady=20, fill=tk.X)

        self.create_info_card(info_frame, "CPU Usage", psutil.cpu_percent(), "%")
        self.create_info_card(info_frame, "Memory", psutil.virtual_memory().percent, "%")
        self.create_info_card(info_frame, "Battery", psutil.sensors_battery().percent, "%")
        self.create_info_card(info_frame, "Brightness", sbc.get_brightness()[0], "%")

        # Quick Actions
        action_frame = ttk.Frame(dash_frame)
        action_frame.pack(pady=20)

        ttk.Button(action_frame, text="Take Screenshot", command=self.take_screenshot).grid(row=0, column=0, padx=10)
        ttk.Button(action_frame, text="Lock System", command=self.lock_system).grid(row=0, column=1, padx=10)
        ttk.Button(action_frame, text="Emergency Restart", command=self.emergency_restart).grid(row=0, column=2,
                                                                                                padx=10)

    def create_media_tab(self):
        media_frame = ttk.Frame(self.notebook)
        self.notebook.add(media_frame, text="Media Control")

        # Volume Control
        vol_frame = ttk.Frame(media_frame)
        vol_frame.pack(pady=20, fill=tk.X)

        ttk.Label(vol_frame, text="Master Volume", font=('Segoe UI', 14, 'bold')).pack()
        self.vol_slider = ttk.Scale(vol_frame, from_=0, to=1,
                                    command=lambda v: self.volume.SetMasterVolumeLevelScalar(float(v), None))
        self.vol_slider.set(self.volume.GetMasterVolumeLevelScalar())
        self.vol_slider.pack(pady=10, fill=tk.X, padx=50)

        # Brightness Control
        bright_frame = ttk.Frame(media_frame)
        bright_frame.pack(pady=20, fill=tk.X)

        ttk.Label(bright_frame, text="Display Brightness", font=('Segoe UI', 14, 'bold')).pack()
        self.bright_slider = ttk.Scale(bright_frame, from_=0, to=100,
                                       command=lambda v: sbc.set_brightness(int(float(v))))
        self.bright_slider.set(sbc.get_brightness()[0])
        self.bright_slider.pack(pady=10, fill=tk.X, padx=50)

    def create_network_tab(self):
        net_frame = ttk.Frame(self.notebook)
        self.notebook.add(net_frame, text="Network Settings")

        # WiFi Controls
        wifi_frame = ttk.Frame(net_frame)
        wifi_frame.pack(pady=20, fill=tk.X)

        ttk.Label(wifi_frame, text="WiFi Controls", font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        self.wifi_status = tk.BooleanVar()
        ttk.Checkbutton(wifi_frame, text="Enable WiFi", variable=self.wifi_status,
                        command=self.toggle_wifi).pack(pady=10, anchor='w')

        # Bluetooth Controls
        bt_frame = ttk.Frame(net_frame)
        bt_frame.pack(pady=20, fill=tk.X)

        ttk.Label(bt_frame, text="Bluetooth Controls", font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        self.bt_status = tk.BooleanVar()
        ttk.Checkbutton(bt_frame, text="Enable Bluetooth", variable=self.bt_status,
                        command=self.toggle_bluetooth).pack(pady=10, anchor='w')

    def create_news_tab(self):
        news_frame = ttk.Frame(self.notebook)
        self.notebook.add(news_frame, text="Live News")

        self.news_canvas = tk.Canvas(news_frame, bg=self.themes[self.theme_mode.get()]['bg'])
        scrollbar = ttk.Scrollbar(news_frame, orient="vertical", command=self.news_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.news_canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.news_canvas.configure(
            scrollregion=self.news_canvas.bbox("all")))

        self.news_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.news_canvas.configure(yscrollcommand=scrollbar.set)

        self.news_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_news(self):
        try:
            api_key = "YOUR_NEWSAPI_KEY"
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
            response = requests.get(url)
            news_data = response.json()

            for idx, article in enumerate(news_data.get('articles', [])):
                self.create_news_card(article, idx)

        except Exception as e:
            print(f"Error fetching news: {e}")

    def create_news_card(self, article, idx):
        card = ttk.Frame(self.scrollable_frame, style='Card.TFrame')
        card.grid(row=idx, column=0, sticky='ew', padx=10, pady=5)

        ttk.Label(card, text=article['title'], font=('Segoe UI', 12, 'bold'), wraplength=800).pack(anchor='w')
        ttk.Label(card, text=article['description'], wraplength=800).pack(anchor='w')
        ttk.Button(card, text="Read More", command=lambda: wb.open(article['url'])).pack(anchor='e')

    def create_info_card(self, parent, title, value, unit):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)

        ttk.Label(card, text=title, font=('Segoe UI', 12, 'bold')).pack()
        ttk.Label(card, text=f"{value}{unit}", font=('Segoe UI', 24, 'bold')).pack()

    def update_clock(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.root.after(1000, self.update_clock)

    def update_system_info(self):
        self.root.after(2000, self.update_system_info)

    def toggle_wifi(self):
        state = "enable" if self.wifi_status.get() else "disable"
        subprocess.run(f"netsh interface set interface 'Wi-Fi' {state}", shell=True)

    def toggle_bluetooth(self):
        # Platform-specific implementation required
        messagebox.showinfo("Info", "Bluetooth control requires platform-specific implementation")

    def take_screenshot(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            pyautogui.screenshot().save(file_path)
            messagebox.showinfo("Success", "Screenshot saved successfully")

    def lock_system(self):
        ctypes.windll.user32.LockWorkStation()

    def emergency_restart(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to emergency restart?"):
            subprocess.call(["shutdown", "/r", "/t", "0"])


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedScreenController(root)
    root.mainloop()