# This module is not used directly within flawcastr.py. It is used to collate all .md and .py files within the central Flawcastr folder/directory into the user clipboard, so the user can paste the full context into an LLM in order to provide context to an LLM when providing instructions.

import os
import pyperclip
import re

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

# Get the directory of the script file
script_directory = os.path.dirname(os.path.abspath(__file__))

# Get all .md and .py files
md_files = [f for f in os.listdir(script_directory) if f.endswith('.md')]
py_files = [f for f in os.listdir(script_directory) if f.endswith('.py')]

# Sort the files
md_files.sort(key=natural_sort_key)
py_files.sort(key=natural_sort_key)

# Create the contents section
contents = "Contents from the following files are collated below (in the following order):\n\n"
for file in md_files + py_files:
    contents += f"* {file}\n"

combined_content = contents + "\n" + "="*50 + "\n\n"

# Process .md files first, then .py files
for file in md_files + py_files:
    file_path = os.path.join(script_directory, file)
    combined_content += f"{'='*50}\n"
    combined_content += f"File: {file_path}\n"
    combined_content += f"{'='*50}\n\n"
    with open(file_path, 'r', encoding='utf-8') as current_file:
        combined_content += current_file.read()
    combined_content += "\n\n"

# Copy the combined content to clipboard
pyperclip.copy(combined_content)

print("Content copied to clipboard!")