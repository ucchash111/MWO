import os
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import simpledialog, filedialog

class ImageRenamerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Renamer")
        self.master.option_add("*Font", ("Helvetica", 12))

        self.image_folder = ""
        self.image_files = []
        self.current_index = 0

        self.create_widgets()

    def create_widgets(self):
        label_font = ("Helvetica", 12)

        tk.Label(self.master, text="Select folder containing images:", font=label_font).pack()
        tk.Button(self.master, text="Browse", command=self.browse_folder, font=label_font).pack()

        self.image_label = tk.Label(self.master, font=label_font)
        self.image_label.pack()

        # Call rename_image automatically after displaying each image
        self.master.after(100, self.rename_image)

    def browse_folder(self):
        self.image_folder = filedialog.askdirectory()
        tk.Label(self.master, text=f"Selected folder: {self.image_folder}").pack()

        # Get a list of image files in the selected folder
        self.image_files = [file for file in os.listdir(self.image_folder) if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

        if not self.image_files:
            tk.Label(self.master, text="No image files found in the selected folder.").pack()
            return

        # Sort the image files by creation time
        self.image_files.sort(key=lambda x: os.path.getctime(os.path.join(self.image_folder, x)))

        # Show the first image
        self.show_image()

    def show_image(self):
        if self.current_index < len(self.image_files):
            image_path = os.path.join(self.image_folder, self.image_files[self.current_index])
            img = Image.open(image_path)
            img.thumbnail((800, 800))  # Resize the image for display
            img_tk = ImageTk.PhotoImage(img)

            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk

            # Automatically call rename_image after a short delay
            self.master.after(0, self.rename_image)
        else:
            tk.Label(self.master, text="No more images to rename.").pack()

    def rename_image(self):
        if self.current_index < len(self.image_files):
            answer_number = simpledialog.askinteger("Input", "Enter the answer number:")
            if answer_number is not None:
                old_path = os.path.join(self.image_folder, self.image_files[self.current_index])
                new_filename = f"answer_{answer_number}.png"
                new_path = os.path.join(self.image_folder, new_filename)

                os.rename(old_path, new_path)
                tk.Label(self.master, text=f"Renamed {self.image_files[self.current_index]} to {new_filename}").pack()

            # Move to the next image
            self.current_index += 1
            self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageRenamerApp(root)
    root.mainloop()
