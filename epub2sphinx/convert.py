import datetime
import ebooklib
import pypandoc
import os
import re
import shutil
import click

from ebooklib import epub

def create_directory_structure(output_directory,working_directories_to_be_created):
    # Abort with error if a directory already exists
    # Else create directories for source and build
    is_directory_present = os.path.isdir(output_directory)
    if is_directory_present:
        error_message="The directory {} should not be present already"
        raise Exception(error_message.format(output_directory))
    for directory_name in working_directories_to_be_created:
        path = os.path.join(output_directory,directory_name)
        os.makedirs(path)

def generate_conf(book, theme, source_directory):
    # Generate conf.py for sphinx by extracting title, author name, etc
    try:
      author = book.get_metadata('DC', 'creator')[0][0]
    except:
      author = None
    with open('templates/conf.py', 'r') as in_conf:
        conf_contents = in_conf.read()

    # Add Author, Theme, Copyright, Title
    conf_contents = conf_contents.replace("<<<TITLE>>>", book.title)
    conf_contents = conf_contents.replace("<<<THEME>>>", theme)
    if author:
        conf_contents = conf_contents.replace("<<<COPYRIGHT>>>", datetime.datetime.now().strftime("%Y") + " " + author)
        conf_contents = conf_contents.replace("<<<AUTHOR>>>", author)
    else:
        conf_contents = conf_contents.replace("copyright = '<<<COPYRIGHT>>>'", "")
        conf_contents = conf_contents.replace("author = '<<<AUTHOR>>>'", "")

    with open(source_directory+'conf.py', 'x') as out_conf:
        out_conf.write(conf_contents)

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

def generate_index(book, dest_dir):
    # Get Author Name
    try:
      author = book.get_metadata('DC', 'creator')[0][0]
    except:
      author = ''

    # Generate index.rst
    with open(f"{dest_dir}/source/index.rst", 'w') as f:
        f.write(f"{book.title}\n")
        f.write("==============================\n\n")
        if author != '':
            f.write(f"Author: {author}\n\n")
            f.write("==============================\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 2\n")
        f.write("   :caption: Contents:\n")
        f.write("   :name: maintoc\n")
        f.write("   :glob:\n\n")
        f.write("   *\n")


def extract_images(input_epub, output_directory):
    source_directory = os.path.join(output_directory, 'source/')

    # save all media, xml, font files for the current book to its source directory
    files = input_epub.get_items()
    for book_file in files:
        try:
            directories = (source_directory + book_file.file_name).split('/')
            if len(directories) > 1:
                directory = "/".join(directories[:-1])
                if not os.path.exists(directory):
                    os.makedirs(directory)

            # file.content is in bytes format
            click.echo(os.path.join(source_directory, book_file.file_name))
            with open(os.path.join(source_directory, book_file.file_name), 'wb') as image_file:
                image_file.write(book_file.content)
        except Exception as error:
            click.echo(error)


def convert_epub(name, output_directory, sphinx_theme_name):
    # Read epub
    input_epub = epub.read_epub(name)
    # Create output directory structure
    create_directory_structure(output_directory,["source","build"])
    # Generate conf.py
    generate_conf(input_epub, sphinx_theme_name, output_directory + '/source/')
    # Copy Makefiles into output_directory
    shutil.copyfile('templates/Makefile', output_directory + '/Makefile')
    shutil.copyfile('templates/make.bat', output_directory + '/make.bat')
    # Generate ReST file for each chapter in ebook
    generate_rst(input_epub, output_directory + '/source/')
    # Generate index.rst
    generate_index(input_epub, output_directory)
    # Extract images from epub
    extract_images(input_epub, output_directory)
