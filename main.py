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

    if len(delimiter) > 20:
        raise ValueError("Delimiter can't be more than 20 characters")
    elif not delimiter.strip():
        raise ValueError("Delimiter can't be blank.")
    # Use regex to find all instances of the question-answer pattern
    question_pattern = fr"(NEW QUESTION|QUESTION)\s+(\d+)\n(.+?)(?=\n[A-Z]\.)"
    answer_pattern = fr"\n([A-Z]\.[\s\S]+?)(?=\n[A-Z]|{delimiter})"
    correct_answer_pattern = fr"({delimiter}):\s*([A-Z])"

    question_matches = re.finditer(question_pattern + answer_pattern + correct_answer_pattern, contents, re.DOTALL)
    qa_list = []
    for match in question_matches:
        question_number = match.group(2)
        question = match.group(3)
        qa_list.append([question_number, question])

        answers_section = match.group(0)
        answer_matches = re.finditer(answer_pattern, answers_section)
        for answer_match in answer_matches:
            answer_symbol = answer_match.group().split(".")[0].strip()
            answer = answer_match.group().split(".")[1].strip()
            qa_list.append([answer_symbol, answer])

        correct_answer_match = re.search(correct_answer_pattern, answers_section)
        correct_answer_symbol = correct_answer_match.group(2)
        qa_list.append(["Answer", correct_answer_symbol])

    return qa_list


# Function to create the Anki deck
def create_anki_deck(qa_list):
    # Create a new Anki deck using the 'anki_deck_template.txt' file
    with open('anki_deck.txt', 'w') as anki_deck:
        for qa in qa_list:
            question = qa[0]
            answer = qa[1]
            anki_deck.write(question + '\t' + answer + '\n')


# Function to create the CSV file
def create_csv(qa_list):
    with open('qa.csv', 'w', newline='') as qa_csv:
        csv_writer = csv.writer(qa_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Number', 'Question/Answer'])
        for qa in qa_list:
            csv_writer.writerow(qa)


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
#
#
# def on_submit():
#     file_path = file_path_entry.get()
#     delimiter = delimiter_entry.get()
#     extract_create(file_path, delimiter)
#     result_label.config(text="Anki Deck and CSV file created!")
#

# if __name__ == '__main__':
#     root = tk.Tk()
#     root.title("Question-Answer Extractor")
#
#     # file_path_
#     # root = tk.Tk()
#
#     # create the widgets
#     file_path_label = tk.Label(root, text="File path:")
#     file_path_entry = tk.Entry(root)
#     select_file_button = tk.Button(root, text="Select file", command=on_select_file)
#     delimiter_label = tk.Label(root, text="Delimiter:")
#     delimiter_entry = tk.Entry(root)
#     submit_button = tk.Button(root, text="Submit", command=on_submit)
#     result_label = tk.Label(root)
#
#     # arrange the widgets
#     file_path_label.grid(row=0, column=0, padx=5, pady=5)
#     file_path_entry.grid(row=0, column=1, padx=5, pady=5)
#     select_file_button.grid(row=0, column=2, padx=5, pady=5)
#     delimiter_label.grid(row=1, column=0, padx=5, pady=5)
#     delimiter_entry.grid(row=1, column=1, padx=5, pady=5)
#     submit_button.grid(row=1, column=2, padx=5, pady=5)
#     result_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
#
#     root.mainloop()
