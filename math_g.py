import os
import json
import time
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import pygame
from PIL import Image, ImageTk
from fuzzywuzzy import fuzz

class ImageSolverApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Solver")
        self.master.option_add("*Font", ("Helvetica", 12))

        # Initialize pygame mixer
        pygame.mixer.init()

        self.script_directory = os.path.dirname(os.path.realpath(__file__))
        self.image_folder = ""
        self.json_file = ""
        self.start_number = 0
        self.end_number = 0
        self.problems = {}

        self.total_solve_time = 0
        self.correct_attempts = 0

        self.create_widgets()

    def create_widgets(self):
        label_font = ("Helvetica", 12)

        tk.Label(self.master, text="Select folder containing images:", font=label_font).pack()
        tk.Button(self.master, text="Browse", command=self.browse_folder, font=label_font).pack()

        tk.Label(self.master, text="Start problem number:", font=label_font).pack()
        self.start_number_entry = tk.Entry(self.master, font=label_font)
        self.start_number_entry.pack()

        tk.Label(self.master, text="End problem number:", font=label_font).pack()
        self.end_number_entry = tk.Entry(self.master, font=label_font)
        self.end_number_entry.pack()

        self.progress_label = tk.Label(self.master, text="", font=label_font)
        self.progress_label.pack()

        self.image_label = tk.Label(self.master, font=label_font)
        self.image_label.pack()

        # Bind the <Return> key to the start_solving method
        self.master.bind('<Return>', lambda event=None: self.start_solving())

        tk.Button(self.master, text="Start", command=self.start_solving, font=label_font).pack()

    def browse_folder(self):
        self.image_folder = filedialog.askdirectory()
        tk.Label(self.master, text=f"Selected folder: {self.image_folder}").pack()

    def start_solving(self):
        self.start_number = int(self.start_number_entry.get())
        self.end_number = int(self.end_number_entry.get())

        self.json_file = os.path.join(self.image_folder, 'answers.json')

        try:
            self.problems = load_json(self.json_file)
        except FileNotFoundError:
            messagebox.showerror("Error", "answers.json not found in the selected folder.")
            return

        for problem_number in range(self.start_number, self.end_number + 1):
            image_path = os.path.join(self.image_folder, f"problem_{problem_number}.png")

            if not os.path.exists(image_path):
                messagebox.showwarning("Warning", f"Image not found for problem {problem_number}. Skipping.")
                continue

            self.show_image(image_path)
            expected_solution = self.problems.get(str(problem_number))
            solve_time = self.solve_problem(expected_solution, problem_number)

            self.total_solve_time += solve_time
            self.correct_attempts += 1

        average_solve_time = self.total_solve_time / self.correct_attempts if self.correct_attempts > 0 else 0
        result_text = f"Average solving time for correct answers: {average_solve_time:.2f} seconds"
        messagebox.showinfo("Results", result_text)

    def show_image(self, image_path):
        img = Image.open(image_path)
        width, height = img.size

        # Calculate the aspect ratio
        aspect_ratio = width / height

        # Set the target width (you can adjust this value)
        target_width = 800

        # Calculate the target height to maintain aspect ratio
        target_height = int(target_width / aspect_ratio)

        img = img.resize((target_width, target_height), Image.LANCZOS)  # Resize the image
        img_tk = ImageTk.PhotoImage(img)

        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk

    def solve_problem(self, expected_solution, problem_number):
        self.progress_label.config(text=f"Solving problem {problem_number}")
        start_time = time.time()
        while True:
            solution = simpledialog.askstring("Input", "Enter the solution to the problem:")
            end_time = time.time()

            if isinstance(expected_solution, (int, float)):
                # If the expected solution is a number, check for an exact match
                try:
                    solution = float(solution)
                    if solution == expected_solution:
                        messagebox.showinfo("Result", "Correct!")
                        self.play_correct_sound()
                        return end_time - start_time
                    else:
                        response = messagebox.askokcancel("Try Again", "Incorrect. Try again.")
                        self.play_wrong_sound()
                        if not response:
                            break
                except ValueError:
                    # If the input is not a valid number, ask for input again
                    messagebox.showerror("Error", "Please enter a valid number.")
            else:
                # Use fuzzy matching to check similarity for text
                similarity_ratio = fuzz.ratio(solution.lower(), str(expected_solution).lower())

                if similarity_ratio >= 90:  # Adjust the threshold as needed
                    messagebox.showinfo("Result", f"Correct  with similarity: {similarity_ratio}!")
                    self.play_correct_sound()
                    return end_time - start_time
                else:
                    response = messagebox.askokcancel("Try Again", f"Incorrect with similarity: {similarity_ratio}. Try again.")
                    self.play_wrong_sound()
                    if not response:
                        break

    def play_correct_sound(self):
        # Load and play the correct sound file
        correct_sound_file = os.path.join(self.script_directory, 'correct_sound.mp3')
        pygame.mixer.music.load(correct_sound_file)
        pygame.mixer.music.play()

    def play_wrong_sound(self):
        # Load and play the correct sound file
        correct_sound_file = os.path.join(self.script_directory, 'wrong_sound.mp3')
        pygame.mixer.music.load(correct_sound_file)
        pygame.mixer.music.play()

def load_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        # Check if each value can be converted to a number, and convert if possible
        for key, value in data.items():
            try:
                float_value = float(value)
                # Check if the float value is actually an integer (e.g., 5.0)
                data[key] = int(float_value) if float_value.is_integer() else float_value
            except ValueError:
                pass  # Ignore if the value cannot be converted to a number
    return data

def save_json(json_file, data):
    with open(json_file, 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSolverApp(root)
    root.mainloop()
