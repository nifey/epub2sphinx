import ebooklib
import pypandoc
import os
import re

from ebooklib import epub

def create_directory_structure(book):
    # Abort with error if a directory already exists
    # Else create directories for source and build
    pass

def generate_conf(book):
    # Generate conf.py for sphinx by extracting title, author name, etc
    pass

def generate_rst(book, source_directory):
    # Generate ReST file for each chapter in ebook
    file_names = []
    rubric_pattern = re.compile(r"\brubric::[ ]+(.+)\n")
    for chapter in book.spine:
        chapter_item = book.get_item_with_id(chapter[0])

        # Save filename for adding to index.rst's toctree
        file_name = chapter_item.get_name()
        file_names.append(file_name)

        # Create any parent directories as given in the filename
        os.makedirs(os.path.dirname(source_directory + file_name), exist_ok=True)

        # Convert HTML to ReST
        html_content = chapter_item.get_content()
        rst_content = pypandoc.convert_text(html_content, 'rst', format='html')

        matches = re.findall(rubric_pattern, rst_content)
        if len(matches) == 0:
            # TODO Check the headings in the file for chapter title
            chapter_title = "Chapter"
        else:
            chapter_title = matches[0]

        with open(source_directory + file_name + '.rst', 'x') as ch_file:
            # Add Chapter title
            ch_file.write('*'*len(chapter_title)+'\n')
            ch_file.write(chapter_title+'\n')
            ch_file.write('*'*len(chapter_title)+'\n')

            # Write ReST content
            ch_file.write(rst_content)

    # Generate index.rst
    generate_index(file_names)

def generate_index(input_epub):
    # Generate index.rst
    pass

def extract_images(input_epub):
    # Extract images from epub
    pass

def convert_epub(name, output_directory, sphinx_theme_name):
    # Read epub
    input_epub = epub.read_epub(name)
    # Create output directory structure
    create_directory_structure(output_directory)
    # Generate conf.py
    generate_conf(input_epub)
    # Generate ReST file for each chapter in ebook
    generate_rst(input_epub, output_directory + '/source/')
    # Generate index.rst
    generate_index(input_epub)
    # Extract images from epub
    extract_images(input_epub)
