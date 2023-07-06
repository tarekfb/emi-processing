import os
from pathlib import Path
import re
import string

def remove_non_ascii(text):
    # Filter out non-printable ASCII characters
    printable_chars = set(string.printable)
    filtered_text = ''.join(filter(lambda c: c in printable_chars, text))
    return filtered_text

def keep_lines_with_empty_previous(lines):
    cleaned_lines = []

    for i in range(len(lines)):
        if i == 0 or lines[i-1].strip() == "":
            cleaned_lines.append(lines[i])

    previous_line_empty = False
    
    cleaned_lines = remove_one_of_two_empty_lines(cleaned_lines)
    
    return cleaned_lines

def remove_one_of_two_empty_lines(lines):
    cleaned_lines = []
    previous_line_empty = False

    for line in lines:
        current_line_empty = line.strip() == ""
        if not (previous_line_empty and current_line_empty):
            cleaned_lines.append(line)
        previous_line_empty = current_line_empty

    return cleaned_lines

def create_emiautoconfiguration_file(lines, newPath):
    with open(newPath, 'w') as file:
        for line in lines:
            file.write(line + '\n')

def replace_after_equal_sign(text, replacement: string):
    parts = text.split("=")
    if len(parts) > 1:
        return parts[0] + "=" + replacement
    return text

def find_next_occurrence(lines, start_string, target_string):
    found_start = False
    for line in lines:
        if not found_start and start_string in line:
            found_start = True
        elif found_start:
            if target_string in line:
                return line
    return None

def find_and_replace(lines: list, start_string, target_string, replacement) -> list:
    found_start = False
    newLine = ''
    index = 0
    for line in lines:
        if not found_start and start_string in line:
            found_start = True
        elif found_start:
            if target_string in line:
                parts = line.split("=")
                if len(parts) > 1:
                    newLine = parts[0] + "=" + replacement
                    lines[index] = newLine
        index += 1
    return lines

def determine_step_degree(lines) -> int:
    targetLine = find_next_occurrence(lines, '[Preview Measurements]', 'PositionStep')
    numerical_values = re.findall(r'\d+', targetLine)
    return numerical_values[0]

def process_file(oldPath, newPath):
    contents = Path(oldPath).read_text()
    contents = remove_non_ascii(contents)
    lines = contents.splitlines()
    lines = keep_lines_with_empty_previous(lines)

    lines = find_and_replace(lines, '[Adjustment]', 'PositionSpeed', '8')
    lines = find_and_replace(lines, '[Adjustment]', 'PositionMeasurementSpeed', '2')

    lines = find_and_replace(lines, '[Preview Measurements]', 'PositionStart', '0')
    step_degree = determine_step_degree(lines) 
    if step_degree == '15':
        lines = find_and_replace(lines, '[Preview Measurements]', 'PositionStop', '345')
    elif step_degree == '30':
        lines = find_and_replace(lines, '[Preview Measurements]', 'PositionStop', '330')
    elif step_degree == '45':
        lines = find_and_replace(lines, '[Preview Measurements]', 'PositionStop', '315')
    else:
        print('No numbers')

    create_emiautoconfiguration_file(lines, newPath)

def process_files(oldFolder, newFolder):
    files = []
    for file_name in os.listdir(oldFolder):
        if os.path.isfile(os.path.join(oldFolder, file_name)):
            files.append(file_name)
    for file in files:
        file_name = os.path.basename(file)
        process_file(oldFolder + '/' + file, newFolder + "/" + file)

print('Welcome! Do you have a folder that ONLY contains your files to be reformatted?')
y = input("Y to continue, N to abort.")
if y == 'y':
    print("When pasting paths, please omit any trailing slashes.")
    old = input("Please paste the location of the current files:\n").strip()
    new = input("Please paste the location for the new files to be placed in:\n").strip()

    if os.path.isdir(old) and os.path.isdir(new):
        process_files(old, new)
        input("All files have been processed. A copy of your files with updated values have been placed in " + new)
    else:
        print('One or both of the paths do not exist.\n ')
    
#python -m PyInstaller script.py
# for dist