import datetime
import ebooklib
import pypandoc
import os
import re
import shutil
import click

from ebooklib import epub

class Converter:
    def __init__(self, file_name, output_directory, sphinx_theme_name):
        self.file = file_name
        self.output_directory = output_directory
        self.source_directory = os.path.join(output_directory, 'source')
        self.theme = sphinx_theme_name

        self.epub = epub.read_epub(file_name)
        self.title = self.epub.title
        try:
          self.author = self.epub.get_metadata('DC', 'creator')[0][0]
        except:
          self.author = None

    def convert(self):
        # Create output directory structure
        click.echo("\nCreating directory structure")
        self.create_directory_structure(["source","build","source/_static"])
        # Generate conf.py
        click.echo("Generating conf.py")
        self.generate_conf()
        # Copy Makefiles into output_directory
        click.echo("Copying Makefiles")
        shutil.copyfile(os.path.join('templates','Makefile'),
                        os.path.join(self.output_directory, 'Makefile'))
        shutil.copyfile(os.path.join('templates','make.bat'),
                        os.path.join(self.output_directory, 'make.bat'))
        # Generate ReST file for each chapter in ebook
        click.echo("Generating ReST files")
        self.generate_rst()
        # Generate index.rst
        click.echo("Generating index.rst")
        self.generate_index()
        # Extract images from epub
        click.echo("Extracting images")
        self.extract_images()

    def create_directory_structure(self, working_directories_to_be_created):
        # Abort with error if a directory already exists
        # Else create directories for source and build
        is_directory_present = os.path.isdir(self.output_directory)
        if is_directory_present:
            error_message="The directory {} should not be present already"
            raise Exception(error_message.format(self.output_directory))
        for directory_name in working_directories_to_be_created:
            path = os.path.join(self.output_directory,directory_name)
            os.makedirs(path)

    def generate_conf(self):
        # Generate conf.py for sphinx by extracting title, author name, etc
        with open('templates/conf.py', 'r') as in_conf:
            conf_contents = in_conf.read()

        # Add Author, Theme, Copyright, Title
        conf_contents = conf_contents.replace("<<<TITLE>>>", self.title)
        conf_contents = conf_contents.replace("<<<THEME>>>", self.theme)
        if self.author:
            conf_contents = conf_contents.replace("<<<COPYRIGHT>>>", datetime.datetime.now().strftime("%Y") + " " + self.author)
            conf_contents = conf_contents.replace("<<<AUTHOR>>>", self.author)
        else:
            conf_contents = conf_contents.replace("copyright = '<<<COPYRIGHT>>>'", "")
            conf_contents = conf_contents.replace("author = '<<<AUTHOR>>>'", "")

        with open(os.path.join(self.source_directory,'conf.py'), 'x') as out_conf:
            out_conf.write(conf_contents)

    def generate_rst(self):
        # Generate ReST file for each chapter in ebook
        file_names = []
        rubric_pattern = re.compile(r"\brubric::[ ]+(.+)\n")
        for chapter in self.epub.spine:
            chapter_item = self.epub.get_item_with_id(chapter[0])

            # Save filename for adding to index.rst's toctree
            file_name = chapter_item.get_name()
            file_names.append(file_name)

            # Create any parent directories as given in the filename
            os.makedirs(os.path.dirname(os.path.join(self.source_directory, file_name)), exist_ok=True)

            # Convert HTML to ReST
            html_content = chapter_item.get_content()
            rst_content = pypandoc.convert_text(html_content, 'rst', format='html')

            matches = re.findall(rubric_pattern, rst_content)
            if len(matches) == 0:
                # TODO Check the headings in the file for chapter title
                chapter_title = "Chapter"
            else:
                chapter_title = matches[0]

            with open(os.path.join(self.source_directory, file_name + '.rst'), 'x') as ch_file:
                # Add Chapter title
                ch_file.write('*'*len(chapter_title)+'\n')
                ch_file.write(chapter_title+'\n')
                ch_file.write('*'*len(chapter_title)+'\n')

                # Write ReST content
                ch_file.write(rst_content)

    def generate_index(self):
        # Generate index.rst
        with open(os.path.join(self.source_directory,"index.rst"), 'w') as f:
            f.write(f"{self.title}\n")
            f.write("==============================\n\n")
            if self.author:
                f.write(f"Author: {self.author}\n\n")
                f.write("==============================\n\n")
            f.write(".. toctree::\n")
            f.write("   :maxdepth: 2\n")
            f.write("   :caption: Contents:\n")
            f.write("   :name: maintoc\n")
            f.write("   :glob:\n\n")
            f.write("   *\n")

    def extract_images(self):
        # save all media, xml, font files for the current book to its source directory
        files = self.epub.get_items()
        for book_file in files:
            try:
                directories = (os.path.join(self.source_directory, book_file.file_name)).split(os.path.sep)
                if len(directories) > 1:
                    directory = os.path.sep.join(directories[:-1])
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                # file.content is in bytes format
                with open(os.path.join(self.source_directory, book_file.file_name), 'wb') as image_file:
                    image_file.write(book_file.content)
            except Exception as error:
                click.echo(error)
