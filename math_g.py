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
        self.current_problem_number = 0  # Add this lineasw

        self.total_solve_time = 0
        self.correct_attempts = 0

        self.entered_solution = None  # New instance variable for entered solution
        self.answer_window = None  # New instance variable for the answer window

        self.create_widgets()

    def show_answer_wrapper(self):
        self.show_answer()
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

        # New button for showing answers
        self.show_answer_button = tk.Button(self.master, text="Show Answer", command=self.show_answer_wrapper)
        self.show_answer_button.pack()


        # New button for hiding the answer
        self.hide_answer_button = tk.Button(self.master, text="Hide Answer", command=self.hide_answer, state=tk.DISABLED)
        self.hide_answer_button.pack()

        # Bind the <Return> key to the start_solving method
        self.master.bind('<Return>', lambda event=None: self.start_solving())

        tk.Button(self.master, text="Start", command=self.start_solving, font=label_font).pack()

    def browse_folder(self):
        self.image_folder = filedialog.askdirectory()
        tk.Label(self.master, text=f"Selected folder: {self.image_folder}").pack()

    def start_solving(self):
        self.start_number = int(self.start_number_entry.get())
        self.end_number = int(self.end_number_entry.get())
    
        for problem_number in range(self.start_number, self.end_number + 1):
            self.current_problem_number = problem_number  # Update the current_problem_number for each problem
    
            self.json_file = os.path.join(self.image_folder, 'answers.json')
    
            try:
                self.problems = load_json(self.json_file)
            except FileNotFoundError:
                messagebox.showerror("Error", "answers.json not found in the selected folder.")
                return
    
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


    def is_solution_correct(self, expected_solution):
        try:
            entered_solution = float(self.entered_solution)
            return entered_solution == expected_solution
        except ValueError:
            similarity_ratio = fuzz.ratio(self.entered_solution.lower(), str(expected_solution).lower())
            return similarity_ratio >= 90

    def solve_problem(self, expected_solution, problem_number):
        self.progress_label.config(text=f"Solving problem {problem_number}")
        start_time = time.time()

        while True:
            # Create a Toplevel window for the input dialog
            input_dialog = tk.Toplevel(self.master)
            input_dialog.title("Input")

            # Entry widget for user input
            solution_entry = tk.Entry(input_dialog, font=("Helvetica", 12))
            solution_entry.pack(pady=10)

            # OK button to submit the solution
            ok_button = tk.Button(input_dialog, text="OK", command=lambda: self.set_solution(solution_entry.get(), input_dialog), font=("Helvetica", 12))
            ok_button.pack()

            input_dialog.wait_window()  # Wait for the input dialog to be closed

            end_time = time.time()

            if self.entered_solution is None:
                messagebox.showerror("Error", f"No solution found for problem {problem_number}.")
                return 0  # Return 0 solve time for problems with no solution

            if self.is_solution_correct(expected_solution):
                messagebox.showinfo("Result", "Correct!")
                self.play_correct_sound()

                # Proceed to the next problem only if the answer is correct
                self.show_answer_button.config(state=tk.NORMAL)
                self.hide_answer_button.config(state=tk.DISABLED)  # Disable hide answer button for the next problem
                self.master.update()

                return end_time - start_time
            else:
                messagebox.showwarning("Incorrect", "Incorrect answer. Please try again.")
                self.play_wrong_sound()

            # Enable the hide answer button after the user has attempted to solve the problem
            self.hide_answer_button.config(state=tk.NORMAL)

            # Force an update to the tkinter window to ensure the "Hide Answer" button is clickable
            self.master.update()

            input_dialog.destroy()
    def show_answer(self):
        problem_number = self.current_problem_number  # Use the current problem number
        answer_image_path = os.path.join(self.image_folder, f"answer_{problem_number}.png")

        if os.path.exists(answer_image_path):
            self.answer_window = tk.Toplevel(self.master)
            self.answer_window.title("Answer")
            answer_img = Image.open(answer_image_path)
            answer_img_tk = ImageTk.PhotoImage(answer_img)

            answer_label = tk.Label(self.answer_window, image=answer_img_tk)
            answer_label.image = answer_img_tk
            answer_label.pack()

            self.show_answer_button.config(state=tk.DISABLED)
            self.hide_answer_button.config(state=tk.NORMAL)  # Enable the hide answer button
        else:
            messagebox.showwarning("Warning", f"Answer image not found for problem {problem_number}.")

    def hide_answer(self):
        if self.answer_window:
            self.answer_window.destroy()

        # Reset the image label to the question image
        question_image_path = os.path.join(self.image_folder, f"problem_{self.current_problem_number}.png")
        self.show_image(question_image_path)

        # Enable the show answer button
        self.show_answer_button.config(state=tk.NORMAL)
        # Disable the hide answer button
        self.hide_answer_button.config(state=tk.DISABLED)

    def set_solution(self, solution, input_dialog):
        # Store the entered solution in the instance variable
        self.entered_solution = solution

        # Destroy the Toplevel window
        input_dialog.destroy()



    def play_correct_sound(self):
        correct_sound_file = os.path.join(self.script_directory, 'correct_sound.mp3')
        pygame.mixer.music.load(correct_sound_file)
        pygame.mixer.music.play()

    def play_wrong_sound(self):
        correct_sound_file = os.path.join(self.script_directory, 'wrong_sound.mp3')
        pygame.mixer.music.load(correct_sound_file)
        pygame.mixer.music.play()

def load_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        for key, value in data.items():
            try:
                float_value = float(value)
                data[key] = int(float_value) if float_value.is_integer() else float_value
            except ValueError:
                pass
    return data

def save_json(json_file, data):
    with open(json_file, 'w') as file:
        json.dump(data, file)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSolverApp(root)
    root.mainloop()
