# MWO (Math Without Overwhelming)

## Introduction
MWO (Math Without Overwhelming) is a Python application that consists of two tools: Image Solver and Screenshot Renamer. The Image Solver tool helps users solve mathematical problems by presenting images and collecting user-input solutions. The Screenshot Renamer tool assists in renaming and collecting answers for a series of screenshots.

## Image Solver
The Image Solver tool is designed to enhance the learning experience by presenting mathematical problems through images. Users can select a folder containing image files, specify the range of problems to solve, and input their answers. The tool provides feedback on correctness and calculates the average solving time for correct answers.

### Usage
1. Run `math_q.py` using Python.
2. Browse and select the folder containing problem images.
3. Specify the start and end problem numbers.
4. Press the "Start" button to begin solving problems.
5. Input your solutions for each problem when prompted.

## Screenshot Renamer
The Screenshot Renamer tool simplifies the process of organizing and collecting answers for a set of screenshots. It allows users to rename the screenshots and input answers for each renamed file, saving the information in a structured JSON format.

### Usage
1. Run `ss_process.py` using Python.
2. Browse and select the folder containing the screenshots.
3. Click the "Start Renaming and Collecting Answers" button.
4. Input answers for each screenshot when prompted.

## Requirements
To run the MWO tools, you need to install the following dependencies:

```bash
pip install pillow pygame fuzzywuzzy
```

Make sure to have Python installed on your system.

## Additional Notes
- For the Image Solver tool, ensure the presence of the correct and wrong sound files (`correct_sound.mp3` and `wrong_sound.mp3`) in the same directory as the script.
- For both tools, it's recommended to organize the files neatly to enhance the user experience.

Feel free to contribute or report issues by creating a pull request or opening an issue on GitHub. Happy problem-solving with MWO!
