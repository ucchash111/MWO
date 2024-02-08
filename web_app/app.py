from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import json
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Assuming images and answers.json are stored in the 'static/images' directory
IMAGE_FOLDER = 'static'

@app.route('/')
def index():
    if 'folder' not in session:
        return redirect(url_for('select_folder'))
    return render_template('index.html')

@app.route('/select_folder', methods=['GET', 'POST'])
def select_folder():
    if request.method == 'POST':
        selected_folder = request.form.get('folder')
        session['folder'] = os.path.join('images', selected_folder)  # Prepend 'images/' to the selected folder
        return redirect(url_for('index'))
    else:
        # List directories inside 'static/images'
        base_path = os.path.join(app.static_folder, 'images')
        folders = [name for name in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, name))]
        return render_template('select_folder.html', folders=folders)

from flask import request, jsonify, session
from PIL import Image, ImageDraw
import base64
import io
import os

@app.route('/save_canvas', methods=['POST'])
def save_canvas():
    data = request.get_json()
    image_data = data['imageData']
    problem_number = data['problemNumber']
    # Assume you're passing the folder name or retrieving it from the session
    # folder_name = data['folderName'] # If passed directly in the request
    folder_name = session.get('folder', 'default_folder')  # Or retrieve from session
    image_data = image_data.split(",")[1]  # Remove the "data:image/png;base64," part

    # Decode the base64 image
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))

    # Create a white background image
    bg = Image.new('RGBA', image.size, (255, 255, 255, 255))
    # Composite the original image onto the white background
    composite = Image.alpha_composite(bg, image.convert('RGBA'))

    # Construct the path to save the image in the same folder as the problem
    folder_path = os.path.join(app.static_folder,  folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f"canvas_problem_{problem_number}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
    file_path = os.path.join(folder_path, filename)

    composite.save(file_path, 'PNG')

    return jsonify({'message': 'Image saved successfully'}), 200


@app.route('/start', methods=['POST'])
def start():
    start_number = int(request.form.get('start_number'))
    end_number = int(request.form.get('end_number'))
    session['answers'] = load_answers(session['folder'])

    # Filter available problems
    available_problems = []
    for num in range(start_number, end_number + 1):
        problem_image_path = os.path.join(session['folder'], f'problem_{num}.png')
        if os.path.isfile(os.path.join(app.static_folder, problem_image_path)) and str(num) in session['answers']:
            available_problems.append(num)

    session['available_problems'] = available_problems
    session['current_index'] = 0  # Index in the available_problems list
    session['correct_times'] = []  # To store times of correct answers
    session['start_time'] = datetime.utcnow().timestamp()  # Store the start time

    if available_problems:
        return redirect(url_for('problem'))
    else:
        return render_template('no_problems_available.html')  # Show a message if no problems are available

@app.route('/problem')
def problem():
    available_problems = session.get('available_problems', [])
    current_index = session.get('current_index', 0)

    if current_index >= len(available_problems):
        # Calculate average time and display the finished page
        if session.get('correct_times'):
            average_time = sum(session['correct_times']) / len(session['correct_times'])
            average_time = "{:.2f}".format(average_time)
        else:
            average_time = "0.00"
        return render_template('finished.html', average_time=average_time)

    current_number = available_problems[current_index]
    return render_template('problem.html', problem_number=current_number)


@app.route('/check_answer', methods=['POST'])
def check_answer():
    entered_answer = request.form.get('answer')
    available_problems = session.get('available_problems', [])
    current_index = session.get('current_index', 0)

    # Ensure we are still within the range of available problems
    if current_index < len(available_problems):
        problem_number = available_problems[current_index]
        correct_answer = session['answers'].get(str(problem_number))
        current_time = datetime.utcnow().timestamp()

        if entered_answer == correct_answer:
            time_taken = current_time - session['start_time']
            session['correct_times'].append(time_taken)  # Store the time taken for this correct answer
            session['start_time'] = current_time  # Reset the start time for the next problem

            # Increment the current index to point to the next available problem
            session['current_index'] += 1

            # Check if all available problems are finished
            if session['current_index'] >= len(available_problems):
                average_time = sum(session['correct_times']) / len(session['correct_times'])
                average_time = "{:.2f}".format(average_time)
                return render_template('finished.html', average_time=average_time)
            
            # Redirect to the next problem
            return redirect(url_for('problem', correct=True))
        else:
            # Incorrect answer, re-render the same problem
            return render_template('problem.html', problem_number=problem_number, error="Incorrect answer. Please try again.", incorrect=True)
    else:
        # All problems have been attempted, show finished page
        return redirect(url_for('finished'))

@app.route('/finished')
def finished():
    if session.get('correct_times'):
        average_time = sum(session['correct_times']) / len(session['correct_times'])
        average_time = "{:.2f}".format(average_time)
    else:
        average_time = "0.00"
    return render_template('finished.html', average_time=average_time)

@app.route('/show_answer')
def show_answer():
    problem_number = session.get('current_number', 0)
    # Build the path to the answer image
    answer_image_filename = f'answer_{problem_number}.png'
    answer_image_path = os.path.join(session['folder'], answer_image_filename)
    # Check if the answer image exists
    if os.path.isfile(os.path.join(app.static_folder, answer_image_path)):
        return render_template('answer.html', problem_number=problem_number, answer_image_path=answer_image_path)
    else:
        # If the answer image doesn't exist, you can redirect to a default page or show a placeholder
        return "Answer image not found", 404

@app.route('/hide_answer')
def hide_answer():
    return redirect(url_for('problem'))

def load_answers(folder_name):
    # The folder_name already contains 'images/', so no need to add it again
    with open(os.path.join(app.static_folder, folder_name, 'answers.json')) as f:
        return json.load(f)

if __name__ == '__main__':
    app.run(port=5000)  # You can choose any available port

