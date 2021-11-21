import pypandoc
import os
import re
import shutil
import click

from .book import Book

templates_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")

def get_chapter_name(chapter):
    if chapter is not None:
        return chapter[0]

class Converter:

    def __init__(self, file_name, output_directory, sphinx_theme_name,include_custom_css):
        self.book = Book(file_name)
        self.output_directory = output_directory
        self.source_directory = os.path.join(output_directory, 'source')
        self.static_files_directory = os.path.join(self.source_directory, '_static')
        self.theme = sphinx_theme_name
        self.include_custom_css = include_custom_css

    def convert(self):
        # Create output directory structure
        click.echo("Creating directory structure")
        self.create_directory_structure(["source","build","source/_static"])
        # Generate conf.py
        click.echo("Generating conf.py")
        self.generate_conf()
        # Copy Makefiles into output_directory
        click.echo("Copying Makefiles")
        shutil.copyfile(os.path.join(templates_directory,'Makefile'),
                        os.path.join(self.output_directory, 'Makefile'))
        shutil.copyfile(os.path.join(templates_directory,'make.bat'),
                        os.path.join(self.output_directory, 'make.bat'))
        # Generate ReST file for each chapter in ebook
        self.generate_rst()
        # Generate index.rst
        click.echo("Generating index.rst")
        self.generate_index()
        # Extract images from epub
        click.echo("Extracting images")
        self.extract_images()

    def create_directory_structure(self, working_directories_to_be_created):
        for directory_name in working_directories_to_be_created:
            path = os.path.join(self.output_directory,directory_name)
            os.makedirs(path)


    def generate_conf(self):
        # Generate conf.py for sphinx by extracting title, author name, etc
        with open(os.path.join(templates_directory, 'conf.py'), 'r') as in_conf:
            conf_contents = in_conf.read()

        # Add Author, Theme, Copyright, Title
        conf_contents = conf_contents.replace("<<<TITLE>>>", self.book.title)
        conf_contents = conf_contents.replace("<<<THEME>>>", self.theme)
        if self.book.author:
            conf_contents = conf_contents.replace("<<<AUTHOR>>>", self.book.author)
        else:
            conf_contents = conf_contents.replace("author = '<<<AUTHOR>>>'", "")
        if self.book.rights:
            conf_contents = conf_contents.replace("<<<COPYRIGHT>>>", self.book.rights)
        else:
            conf_contents = conf_contents.replace("copyright = '<<<COPYRIGHT>>>'", "")

        with open(os.path.join(self.source_directory,'conf.py'), 'x') as out_conf:
            out_conf.write(conf_contents)

    def generate_rst(self):
        # Generate ReST file for each chapter in ebook
        href_pattern = re.compile(r"(href=[\"\'][\w/.@-]*html)([#\'\"])")
        svg_pattern = re.compile(r"\<svg[^\>]*\>(.*)\</svg\>", re.MULTILINE|re.DOTALL)
        with click.progressbar(self.book.epub.spine,show_eta=True,label="Generating ReST files",item_show_func=get_chapter_name) as bar:
            for chapter in bar:
                chapter_item = self.book.epub.get_item_with_id(chapter[0])
                file_name = chapter_item.get_name()
                if file_name in self.book.chapter_names.keys():
                    chapter_title = self.book.chapter_names[file_name]
                else:
                    chapter_title = "Front page"

                # Add filename to toctree
                self.book.toctree.append(file_name)

                # Create any parent directories as given in the filename
                os.makedirs(os.path.dirname(os.path.join(self.source_directory, file_name)), exist_ok=True)

                # Convert HTML to ReST
                html_content = chapter_item.get_content().decode()
                html_content = re.sub(href_pattern, r"\1.html\2", html_content)
                if html_content.find("epub:type") != -1:
                    self.book.toctree.remove(file_name)
                    continue
                if html_content.find("<svg") != -1:
                    html_content = re.sub(svg_pattern, r"\1", html_content)
                    html_content = html_content.replace("<image", "<img").replace("xlink:href", "src")
                rst_content = pypandoc.convert_text(html_content, 'rst', format='html')

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
            f.write(f"{self.book.title}\n")
            f.write(f"{'='*len(self.book.title)}\n\n")
            if self.book.author:
                f.write(f"Author: {self.book.author}\n\n")
                f.write("==============================\n\n")
            f.write(".. toctree::\n")
            f.write("   :maxdepth: 1\n")
            f.write("   :caption: Contents:\n")
            f.write("   :name: maintoc\n\n")
            for chapter in self.book.toctree:
                f.write(f"   {chapter}\n")
            f.write("\nIndices\n")
            f.write("==============================\n\n")
            f.write("* :ref:`search`")

    def extract_images(self):
        # save all media, xml, font files for the current book to its source directory
        files = self.book.epub.get_items()
        html_css_files = []

        for book_file in files:
            if book_file.media_type == 'application/xhtml+xml':
                continue
            try:
                file_name = os.path.split(book_file.file_name)[-1]

                directories = (os.path.join(self.source_directory, book_file.file_name)).split(os.path.sep)
                if len(directories) > 1:
                    directory = os.path.sep.join(directories[:-1])
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                file_path = os.path.join(self.source_directory, book_file.file_name)
                if book_file.media_type == 'text/css':
                    if self.include_custom_css:
                        # write css files to the _static directory
                        file_path = os.path.join(self.static_files_directory, file_name)
                        html_css_files.append(file_name)
                    else:
                        continue
                # file.content is in bytes format
                with open(file_path, 'wb') as ext_file:
                    ext_file.write(book_file.content)
            except Exception as error:
                click.echo(error)

        # include the css file paths to the conf file
        if html_css_files:
            with open(os.path.join(self.source_directory, 'conf.py'), 'a') as conf_file:
                conf_file.write(f"html_css_files = {html_css_files}")
