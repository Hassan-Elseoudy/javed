import csv
import re

import PyPDF2


# Function to extract questions and answers from the input file
def extract_qa(file_path, delimiter):
    try:
        if file_path.endswith('.pdf'):
            pdfFileObj = open(file_path, 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            contents = ""
            for i in range(0, pdfReader.numPages):
                contents += pdfReader.getPage(i).extractText()
        elif file_path.endswith(('.txt', '.rtf')):
            with open(file_path, 'r') as file:
                contents = file.read()
        else:
            raise ValueError("Invalid file format. Please select a PDF, txt, or rtf file.")
    except IOError:
        raise ValueError("Error opening the file. Please check the file path and try again.")

    contents = contents.replace("Visit and Download Full Version Exam Dumps", "")
    contents = contents.replace("http://www.certleader.com/CISSP-dumps.html", "")
    contents = contents.replace("CISSP - Certified Information Systems Security Professional (CISSP)", "")
    contents = contents.replace("The Leader of IT Certification", "")
    contents = contents.replace("visit - http://www.certleader.com", "")
    contents = contents.replace("Visit and Download Full Version CISSP Exam Dumps", "")

    if len(delimiter) > 20:
        raise ValueError("Delimiter can't be more than 20 characters")
    elif not delimiter.strip():
        raise ValueError("Delimiter can't be blank.")
    # Use regex to find all instances of the question-answer pattern
    question_pattern = r"(NEW QUESTION|QUESTION)\s(\d+)\n((.|\n)*?)((?:\n[A-D]..+){0})\n"
    correct_answer_pattern = fr"{delimiter}:\s\w"
    question_matches = re.finditer(question_pattern + correct_answer_pattern, contents, re.DOTALL)
    qa_list = []
    for match in question_matches:
        question_number = match.group(2)
        question = match.group(3)
        answers_section = match.group(0)

        correct_answer_match = re.search(correct_answer_pattern, answers_section)
        correct_answer_symbol = correct_answer_match.group(0)
        qa_list.append(
            ["\n".join([question_number, "<br></br>".join(question.split("\n")), "<br></br>"]),
             correct_answer_symbol])

    return qa_list


# Function to create the Anki deck
def create_anki_deck(qa_list):
    # Create a new Anki deck using the 'anki_deck_template.txt' file
    with open('anki_deck.txt', 'w') as anki_deck:
        for qa in filter(lambda q: q[1][-1] != 'N', qa_list):
            question = qa[0]
            answer = qa[1]
            anki_deck.write(question + '\n' + answer + '\t')


def create_csv(qa_list):
    with open('qa.csv', 'w', newline='') as qa_csv:
        csv_writer = csv.writer(qa_csv, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Question/Answer', 'Correct Answer'])
        for qa in filter(lambda q: q[1][-1] != 'N', qa_list):
            question_answer = qa[0]
            correct_answer = qa[1]
            csv_writer.writerow([question_answer, correct_answer])


# Function to extract and create file
def extract_create(file_path, delimiter):
    qa_list = extract_qa(file_path, delimiter)
    create_anki_deck(qa_list)
    create_csv(qa_list)


extract_create("javed.txt", "Answer")

# def on_select_file():
#     filepath = filedialog.askopenfilename()
#     file_path_entry.delete(0, tk.END)
#     file_path_entry.insert(0, filepath)


# def on_submit():
#     file_path = file_path_entry.get()
#     delimiter = delimiter_entry.get()
#     extract_create(file_path, delimiter)
#     result_label.config(text="Anki Deck and CSV file created!")
#
#
# root = tk.Tk()
# root.title("Question-Answer Extractor")
#
# # file_path_
# # root = tk.Tk()
#
# # create the widgets
# file_path_label = tk.Label(root, text="File path:")
# file_path_entry = tk.Entry(root)
# select_file_button = tk.Button(root, text="Select file", command=on_select_file)
# delimiter_label = tk.Label(root, text="Delimiter:")
# delimiter_entry = tk.Entry(root)
# submit_button = tk.Button(root, text="Submit", command=on_submit)
# result_label = tk.Label(root)
#
# # arrange the widgets
# file_path_label.grid(row=0, column=0, padx=5, pady=5)
# file_path_entry.grid(row=0, column=1, padx=5, pady=5)
# select_file_button.grid(row=0, column=2, padx=5, pady=5)
# delimiter_label.grid(row=1, column=0, padx=5, pady=5)
# delimiter_entry.grid(row=1, column=1, padx=5, pady=5)
# submit_button.grid(row=1, column=2, padx=5, pady=5)
# result_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
#
# root.mainloop()
