import os
import json
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox

class ScreenshotRenamerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screenshot Renamer and Answer Collector")
        self.screenshot_folder = ""
        self.screenshot_paths = []
        self.answers = {}

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Select the folder containing screenshots:").pack()
        tk.Button(self.master, text="Browse", command=self.browse_folder).pack()

        tk.Button(self.master, text="Start Renaming and Collecting Answers", command=self.start_processing).pack()

    def browse_folder(self):
        self.screenshot_folder = filedialog.askdirectory(title="Select Screenshot Folder")
        if self.screenshot_folder:
            tk.Label(self.master, text=f"Selected Folder: {self.screenshot_folder}").pack()
            self.load_screenshots()

    def load_screenshots(self):
        # Get all image files in the folder and sort them by creation time
        image_files = [f for f in os.listdir(self.screenshot_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        image_files.sort(key=lambda f: os.path.getctime(os.path.join(self.screenshot_folder, f)))

        self.screenshot_paths = [os.path.join(self.screenshot_folder, f) for f in image_files]

    def start_processing(self):
        if not self.screenshot_folder or not self.screenshot_paths:
            messagebox.showerror("Error", "Please select a valid screenshot folder.")
            return

        for idx, screenshot_path in enumerate(self.screenshot_paths):
            # Rename the screenshot file
            new_filename = f"problem_{idx + 1}.png"
            new_filepath = os.path.join(self.screenshot_folder, new_filename)
            os.rename(screenshot_path, new_filepath)

            # Display the screenshot along with the file name
            self.display_screenshot(new_filepath, new_filename)

            # Prompt user for the answer
            answer = simpledialog.askstring("Input", f"Enter the answer to {new_filename}:")
            if answer is None:  # If user clicks cancel
                break

            # Save the answer
            self.answers[str(idx + 1)] = answer

        # Save answers to a JSON file
        answers_file_path = os.path.join(self.screenshot_folder, "answers.json")
        with open(answers_file_path, 'w') as json_file:
            json.dump(self.answers, json_file, indent=2)

        messagebox.showinfo("Info", f"Answers saved to {answers_file_path}")

    def display_screenshot(self, screenshot_path, filename):
        img = Image.open(screenshot_path)
        # Resize for display while maintaining aspect ratio
        width, height = img.size
        target_width = 800
        target_height = int(target_width * height / width)
        img = img.resize((target_width, target_height), Image.ANTIALIAS)
        img_tk = ImageTk.PhotoImage(img)
    
        # Create a new window for displaying the screenshot
        display_window = tk.Toplevel(self.master)
        display_window.title(f"Screenshot: {filename}")
    
        # Display the screenshot in the new window
        label = tk.Label(display_window, image=img_tk)
        label.image = img_tk
        label.pack()
    
        # Display the filename in the new window
        filename_label = tk.Label(display_window, text=f"Current file: {filename}")
        filename_label.pack()
    
        # Prompt user for the answer
        answer = simpledialog.askstring("Input", f"Enter the answer to {filename}:")
    
        # Destroy the window after 1 second
        self.master.after(1000, display_window.destroy)
    
        # Save the answer
        self.answers[str(len(self.answers) + 1)] = answer


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotRenamerApp(root)
    root.mainloop()
