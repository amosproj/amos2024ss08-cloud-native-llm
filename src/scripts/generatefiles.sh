#!/bin/bash

# Number of PDF files to create
num_files=5

# Create Markdown files with random names and fill them with random text
for ((i=1; i<=$num_files; i++)); do
    # Generate a random filename with .md extension
    filename=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1).md

    # Generate random text for the Markdown file
    text=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 100 | head -n 1)

    # Write the random text to the Markdown file
    echo "# Random Markdown File $i" > $filename
    echo >> $filename
    echo "This is a random Markdown file created for testing purposes." >> $filename
    echo >> $filename
    echo "Random text: $text" >> $filename

    echo "Created $filename"

    # Convert Markdown file to PDF using pandoc
    pandoc $filename -o "${filename%.md}.pdf"

    echo "Converted ${filename%.md}.pdf"
done
