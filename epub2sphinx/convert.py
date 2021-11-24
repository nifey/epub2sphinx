import jinja2
import os
import shutil
import click

from .book import Book
from .chapter import Chapter
from jinja2 import Environment, PackageLoader

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
        shutil.copytree(os.path.join(templates_directory,"makefiles"),
                        self.output_directory)
        os.makedirs(self.static_files_directory)
        # Generate ReST file for each chapter in ebook
        self.generate_rst()
        # Extract images from epub
        click.echo("Extracting images")
        self.extract_images()
        # Render jinja templates
        click.echo("Generating conf.py and index.rst")
        jinja_env = Environment(
            loader=PackageLoader("epub2sphinx")
        )
        with open(os.path.join(self.source_directory,'conf.py'), 'x') as cf:
            cf.write(jinja_env.get_template('conf.py').render(book=self.book, theme=self.theme))
        with open(os.path.join(self.source_directory,'index.rst'), 'x') as of:
            of.write(jinja_env.get_template('index.rst').render(book=self.book))

    def generate_rst(self):
        # Generate ReST file for each chapter in ebook
        with click.progressbar(self.book.epub.spine,show_eta=True,label="Generating ReST files",item_show_func=get_chapter_name) as bar:
            for chapter_id in bar:
                chapter = Chapter(self.book, chapter_id[0])

                # Add filename to toctree
                self.book.toctree.append(chapter.file)

                # Create any parent directories as given in the filename
                os.makedirs(os.path.dirname(os.path.join(self.source_directory, chapter.file)), exist_ok=True)

                # Convert HTML to ReST
                if not chapter.convert():
                    # Omit chapter from toctree
                    self.book.toctree.remove(chapter.file)
                    continue

                chapter.write(self.source_directory)

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
