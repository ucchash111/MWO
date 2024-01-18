from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import json
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



@app.route('/start', methods=['POST'])
def start():
    start_number = int(request.form.get('start_number'))
    end_number = int(request.form.get('end_number'))
    session['current_number'] = start_number
    session['end_number'] = end_number
    session['correct_times'] = []  # To store times of correct answers
    session['start_time'] = datetime.utcnow().timestamp()  # Store the start time
    session['answers'] = load_answers(session['folder'])
    return redirect(url_for('problem'))

@app.route('/problem')
def problem():
    current_number = session.get('current_number', 0)
    end_number = session.get('end_number', 0)

    if current_number > end_number:
        if session.get('correct_times'):
            average_time = sum(session['correct_times']) / len(session['correct_times'])
            # Format average_time to two decimal places
            average_time = "{:.2f}".format(average_time)
        else:
            average_time = "0.00"
        return render_template('finished.html', average_time=average_time)
    
    return render_template('problem.html', problem_number=current_number)


@app.route('/check_answer', methods=['POST'])
def check_answer():
    entered_answer = request.form.get('answer')
    problem_number = session.get('current_number', 0)
    correct_answer = session['answers'].get(str(problem_number))
    current_time = datetime.utcnow().timestamp()

    if entered_answer == correct_answer:
        time_taken = current_time - session['start_time']
        session['correct_times'].append(time_taken)  # Store the time taken for this correct answer
        session['start_time'] = current_time  # Reset the start time for the next problem

        # Increment the current problem number
        session['current_number'] += 1

        # Check if it's time to finish
        if session['current_number'] > session['end_number']:
            average_time = sum(session['correct_times']) / len(session['correct_times'])
            # Format average_time to two decimal places
            average_time = "{:.2f}".format(average_time)
            return render_template('finished.html', average_time=average_time)

        return render_template('problem.html', problem_number=session['current_number'], correct=True)
    else:
        return render_template('problem.html', problem_number=problem_number, error="Incorrect answer. Please try again.", incorrect=True)

@app.route('/finished')
def finished():
    correct_times = session.get('correct_times', [])
    average_time = sum(correct_times) / len(correct_times) if correct_times else 0
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

