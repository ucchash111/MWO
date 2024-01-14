import json
import os
import time
from PIL import Image

def load_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    return data

def show_image(image_path):
    img = Image.open(image_path)
    img.show()

def solve_problem(expected_solution):
    start_time = time.time()
    while True:
        solution = input("Enter the solution to the problem: ")
        end_time = time.time()

        if solution == expected_solution:
            print("Correct!\n")
            return end_time - start_time
        else:
            print("Incorrect. Try again.\n")

def main():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    image_folder = input("Enter the name of the folder containing images: ")
    image_folder_path = os.path.join(script_directory, image_folder)
    json_file = os.path.join(image_folder_path, 'answers.json')

    start_number = int(input("Enter the start problem number: "))
    end_number = int(input("Enter the end problem number: "))

    problems = load_json(json_file)

    total_solve_time = 0
    correct_attempts = 0

    for problem_number in range(start_number, end_number + 1):
        image_path = os.path.join(image_folder_path, f"problem_{problem_number}.png")

        if not os.path.exists(image_path):
            print(f"Image not found for problem {problem_number} at path: {image_path}. Skipping.")
            continue

        show_image(image_path)
        expected_solution = problems.get(str(problem_number))
        solve_time = solve_problem(expected_solution)

        total_solve_time += solve_time
        correct_attempts += 1

    average_solve_time = total_solve_time / correct_attempts if correct_attempts > 0 else 0
    print(f"Average solving time for correct answers: {average_solve_time:.2f} seconds")

if __name__ == "__main__":
    main()
