import os
import time
import threading
import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# === CONFIG ===
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')
ICON_URL = os.getenv('ICON_URL')

# === Setup ===
root = tk.Tk()
root.title("Weather App")
root.geometry("600x450")
root.resizable(False, False)

# === Load background ===
bg_image = Image.open("background.jpg").resize((600, 450))
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo) # type: ignore
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# === Simulated Blurred Glass Panel ===
blurred = bg_image.crop((80, 180, 520, 370)).filter(ImageFilter.GaussianBlur(8))
blurred_photo = ImageTk.PhotoImage(blurred)
blur_label = tk.Label(root, image=blurred_photo, bd=0) # type: ignore
blur_label.place(x=80, y=180)

# === Weather Result Card ===
card = tk.Frame(root, bg="#000000", bd=0)
card.place(x=80, y=180, width=440, height=190)

# === UI Elements ===
title = tk.Label(root, text="🌦️ Weather App", font=("Helvetica", 20, "bold"),
                 fg="white")
title.place(relx=0.5, y=30, anchor="center")

city_entry = tk.Entry(root, font=("Helvetica", 13), width=28,
                      bg="#222222", fg="gray", insertbackground='white', relief="flat")
city_entry.insert(0, "Enter city name")
city_entry.place(relx=0.5, y=80, anchor="center", height=30)


def on_entry_click(event):
    if city_entry.get() == 'Enter city name':
        city_entry.delete(0, "end")
        city_entry.config(fg='white')


def on_focusout(event):
    if city_entry.get() == '':
        city_entry.insert(0, 'Enter city name')
        city_entry.config(fg='gray')


city_entry.bind('<FocusIn>', on_entry_click)
city_entry.bind('<FocusOut>', on_focusout)

search_button = tk.Button(root, text="Get Weather", command=lambda: get_weather(city_entry.get()),
                          bg="#1e90ff", fg="black", font=("Helvetica", 12, "bold"),
                          activebackground="#3399ff", relief="flat", bd=0, padx=10, pady=5)
search_button.place(relx=0.5, y=130, anchor="center")

result_label = tk.Label(card, text="", font=("Helvetica", 12),
                        bg="#000000", fg="white", justify="left", wraplength=400)
result_label.place(relx=0.5, rely=0.5, anchor="center")

icon_label = tk.Label(card, bg="#000000")
icon_label.place(x=10, y=10)

# === Clock ===
clock_label = tk.Label(root, font=("Courier", 12), bg="#000000", fg="white")
clock_label.place(x=10, y=10)


def update_clock():
    current_time = time.strftime('%H:%M:%S')
    clock_label.config(text=f"🕒 {current_time}")
    root.after(1000, update_clock)


update_clock()

# === Icon Downloader ===
def get_weather_icon(icon_code):
    icon_path = f"weather_icons/{icon_code}.png"
    if not os.path.exists("weather_icons"):
        os.makedirs("weather_icons")
    if not os.path.exists(icon_path):
        try:
            response = requests.get(ICON_URL.format(icon_code))
            with open(icon_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print("Error downloading icon:", e)
            return None
    return ImageTk.PhotoImage(Image.open(icon_path))


# === Typing Animation ===
def type_text(text):
    result_label.config(text="")
    for i in range(len(text) + 1):
        result_label.config(text=text[:i])
        root.update()
        time.sleep(0.01)


# === Fetch Weather Logic ===
def fetch_weather(city):
    try:
        response = requests.get(BASE_URL, params={
            'q': city,
            'appid': API_KEY,
            'units': 'metric'
        }, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            weather = data['weather'][0]['description'].title()
            city_name = data['name']
            country = data['sys']['country']
            icon_code = data['weather'][0]['icon']

            icon = get_weather_icon(icon_code)
            if icon:
                icon_label.config(image=icon)
                icon_label.image = icon

            result = f"📍 {city_name}, {country}\n🌡️ {temp}°C\n🌤️ {weather}"
        else:
            icon_label.config(image="")
            result = "⚠️ City not found."

    except requests.exceptions.Timeout:
        icon_label.config(image="")
        result = "⚠️ Request timed out."
    except Exception as e:
        icon_label.config(image="")
        result = f"⚠️ Error: {e}"

    type_text(result)


def get_weather(city):
    if not city or city.strip() == "" or city == "Enter city name":
        messagebox.showwarning("Input Required", "Please enter a city name.")
        return
    threading.Thread(target=fetch_weather, args=(city,), daemon=True).start()


root.mainloop()
