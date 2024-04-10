import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def on_button_click():
    entry_text = entry.get()
    label.config(text=f"You entered: {entry_text}")

root = tk.Tk()
root.title("Foreground Image Example")

# Load background image
bg_image = Image.open("rpi.jpg")  # Replace "background.jpg" with your image file
bg_photo = ImageTk.PhotoImage(bg_image)
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Create a frame for organizing widgets
main_frame = ttk.Frame(root)
main_frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

# Add widgets to the frame
label = ttk.Label(main_frame, text="Enter text:", font=("Helvetica", 14))
label.pack(pady=20)

entry = ttk.Entry(main_frame, width=30, font=("Helvetica", 12))
entry.pack(pady=10)

button = ttk.Button(main_frame, text="Submit", command=on_button_click)
button.pack(pady=10)

# Create a Canvas widget to hold the foreground image
canvas = tk.Canvas(main_frame, width=600, height=500)
canvas.pack(pady=20)

# Load foreground image
fg_image = Image.open("E_PI_White_good.png")  # Replace "foreground.png" with your image file
fg_photo = ImageTk.PhotoImage(fg_image)

# Place the foreground image on the canvas
canvas.create_image(0, 0, anchor=tk.NW, image=fg_photo)

root.mainloop()
