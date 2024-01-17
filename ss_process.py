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
        self.photo_images = []  # List to store PhotoImage objects
        self.display_window = None  # Reference to the display window
        self.default_answer = "p"  # Default answer value

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
        # Get all image files in the folder
        image_files = [f for f in os.listdir(self.screenshot_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

        # Sort the image files by creation time
        image_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.screenshot_folder, f)))

        self.screenshot_paths = [os.path.join(self.screenshot_folder, f) for f in image_files]

    def start_processing(self):
        if not self.screenshot_folder or not self.screenshot_paths:
            messagebox.showerror("Error", "Please select a valid screenshot folder.")
            return

        for screenshot_path in self.screenshot_paths:
            # Display the screenshot along with the file name and prompt for answer
            filename = os.path.basename(screenshot_path)
            self.display_screenshot(screenshot_path, filename)

        # Save collected answers to a JSON file
        self.save_answers_to_json()

    def save_answers_to_json(self):
        json_file = os.path.join(self.screenshot_folder, 'answers.json')
        with open(json_file, 'w') as file:
            json.dump(self.answers, file)

    def display_screenshot(self, screenshot_path, filename):
        img = Image.open(screenshot_path)
        # Resize for display while maintaining aspect ratio
        width, height = img.size
        target_width = 800
        target_height = int(target_width * height / width)
        img = img.resize((target_width, target_height), Image.ANTIALIAS)
        photo_image = ImageTk.PhotoImage(img)
        self.photo_images.append(photo_image)  # Add PhotoImage to the list
    
        # Destroy the existing window before creating a new one
        if self.display_window:
            self.display_window.destroy()
    
        # Create a new window for displaying the screenshot
        self.display_window = tk.Toplevel(self.master)
        self.display_window.title(f"Screenshot: {filename}")
        label = tk.Label(self.display_window, image=photo_image)
        label.image = photo_image
        label.pack()
    
        # Prompt user for the problem number
        problem_number = self.get_user_input(f"Enter the problem number for {filename}:", default=str(len(self.answers) + 1))
    
        # Destroy the window if user clicks cancel
        if problem_number is None:
            self.display_window.destroy()
            return
    
        # Rename the screenshot file based on the problem number
        new_filename = f"problem_{problem_number}.png"
        new_filepath = os.path.join(self.screenshot_folder, new_filename)
        
        if os.path.exists(new_filepath):
            print(f"Overwriting: {filename} -> {new_filename}")
        else:
            print(f"Renaming: {filename} -> {new_filename}")

        os.rename(screenshot_path, new_filepath)
    
        # Display the filename in the window
        filename_label = tk.Label(self.display_window, text=f"Current file: {new_filename}")
        filename_label.pack()
    
        # Prompt user for the answer
        answer = self.get_user_input(f"Enter the answer to problem {problem_number}:", default=self.default_answer)
    
        # Destroy the window if user clicks cancel
        if answer is None:
            self.display_window.destroy()
            return
    
        # Save the answer
        self.answers[problem_number] = answer
        self.default_answer = "p"  # Reset default answer for the next entry

    def get_user_input(self, prompt, default):
        input_value = simpledialog.askstring("Input", prompt, initialvalue=default)
        self.default_answer = "" if input_value == default else "p"  # If input is changed, remove default
        return input_value

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotRenamerApp(root)
    root.mainloop()
