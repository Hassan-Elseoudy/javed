import csv
import re
import tkinter as tk
from tkinter import filedialog

import PyPDF2


def extract_single_qa(content, delimiter):
    question_pattern = r"(NEW QUESTION|QUESTION)\s+(\d+):*((.)*?)((?:[A-D]..+){0})"
    correct_answer_pattern = fr"{delimiter}:\s\w(.)*"
    question_matches = re.finditer(question_pattern + correct_answer_pattern, content, re.DOTALL)
    for match in question_matches:
        if len(match.groups()) >= 3:
            question_number = match.group(2)
            question = match.group(3)
            answers_section = match.group(0)

            correct_answer_match = re.search(correct_answer_pattern, answers_section)
            correct_answer_symbol = correct_answer_match.group(0)
            # Handling empty Answers.
            if not re.match(fr"{delimiter}:\s+[A-D]", correct_answer_symbol):
                continue
            for alpha in ['A.', 'B.', 'C.', 'D.']:
                question = question.replace(alpha, f"\n{alpha}")
            return ["\n".join([question_number, "<br></br>".join(question.split("\n")), "<br></br>"]),
                    "<br></br>".join(correct_answer_symbol.split("\n"))]
        else:
            print("[WARNING] - Invalid Question Format: Incorrect value for question")
            continue


def extract_qa(file_path, delimiter):
    # Check if the file path is valid
    try:
        contents = "\n"
        if not file_path:
            raise ValueError("File path cannot be empty.")
        if not file_path.endswith(('.pdf', '.txt', '.rtf')):
            raise ValueError("Invalid file format. Please select a PDF, txt, or rtf file.")
        if len(delimiter) > 20:
            raise ValueError("Delimiter can't be more than 20 characters.")
        elif not delimiter.strip():
            raise ValueError("Delimiter can't be blank.")

        # Open the file
        if file_path.endswith('.pdf'):
            pdfFileObj = open(file_path, 'rb')
            pdfReader = PyPDF2.PdfReader(pdfFileObj)
            for i in range(len(pdfReader.pages)):
                contents += pdfReader.pages[i].extract_text()
        elif file_path.endswith(('.txt', '.rtf')):
            with open(file_path, 'r') as file:
                contents += file.read()

    except ValueError as e:
        raise e
    except IOError:
        raise ValueError("Error opening the file. Please check the file path and try again.")

    # Clean the contents
    contents = contents.replace("Visit and Download Full Version Exam Dumps", "")
    contents = contents.replace("http://www.certleader.com/CISSP-dumps.html", "")
    contents = contents.replace("CISSP - Certified Information Systems Security Professional (CISSP)", "")
    contents = contents.replace("The Leader of IT Certification", "")
    contents = contents.replace("visit - http://www.certleader.com", "")
    contents = contents.replace("Visit and Download Full Version CISSP Exam Dumps", "")
    contents = contents.replace("\n", "")

    # Use regex to find all instances of the question-answer pattern
    qa_list = []

    if len(contents.split("NEW QUESTION")) > 1:
        for content in contents.split("NEW QUESTION"):
            if content:
                qa_list.append(extract_single_qa("NEW QUESTION " + content, delimiter))

    elif len(contents.split("QUESTION")) > 1:
        for content in contents.split("QUESTION"):
            if content:
                qa_list.append(extract_single_qa("QUESTION" + content, delimiter))

    return qa_list


def create_csv(qa_list):
    # Check if the qa_list is valid
    if not qa_list:
        raise ValueError("qa_list cannot be empty.")

    try:
        # Open the CSV file
        with open('qa.csv', 'w', newline='') as qa_csv:
            csv_writer = csv.writer(qa_csv, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Question/Answer', 'Correct Answer'])
            # Iterate through the qa_list and add validation for each item
            for qa in qa_list:
                if not qa or len(qa) != 2:
                    print("[WARNING] - Invalid Question Format: Each item in the qa_list must be a tuple of length 2.")
                    continue
                question_answer, correct_answer = qa
                if not question_answer or not correct_answer:
                    print("[WARNING] - Invalid Question Format: Question/Answer and Correct Answer cannot be empty.")
                    continue
                csv_writer.writerow([question_answer, correct_answer])
    except IOError:
        raise ValueError("Error opening the file. Please check the file path and try again.")


# Function to extract and create file
def extract_create(file_path, delimiter):
    qa_list = extract_qa(file_path, delimiter)
    create_csv(qa_list)


def on_select_file():
    filepath = filedialog.askopenfilename()
    file_path_entry.delete(0, tk.END)
    file_path_entry.insert(0, filepath)


def on_submit():
    file_path = file_path_entry.get()
    delimiter = delimiter_entry.get()
    extract_create(file_path, delimiter)
    result_label.config(text="Anki Deck and CSV file created!")


root = tk.Tk()
root.title("Question-Answer Extractor")

# file_path_
# root = tk.Tk()

# create the widgets
file_path_label = tk.Label(root, text="File path:")
file_path_entry = tk.Entry(root)
select_file_button = tk.Button(root, text="Select file", command=on_select_file)
delimiter_label = tk.Label(root, text="Delimiter:")
delimiter_entry = tk.Entry(root)
submit_button = tk.Button(root, text="Submit", command=on_submit)
result_label = tk.Label(root)

# arrange the widgets
file_path_label.grid(row=0, column=0, padx=5, pady=5)
file_path_entry.grid(row=0, column=1, padx=5, pady=5)
select_file_button.grid(row=0, column=2, padx=5, pady=5)
delimiter_label.grid(row=1, column=0, padx=5, pady=5)
delimiter_entry.grid(row=1, column=1, padx=5, pady=5)
submit_button.grid(row=1, column=2, padx=5, pady=5)
result_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
