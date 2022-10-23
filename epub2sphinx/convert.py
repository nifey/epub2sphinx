import ebooklib
import os
import shutil
import click

from .book import Book
from .chapter import Chapter
from concurrent.futures import ThreadPoolExecutor
from jinja2 import Environment, PackageLoader
from tqdm import tqdm

STYLE_TYPES = (ebooklib.ITEM_STYLE, ebooklib.ITEM_FONT)
IMAGE_TYPES = (ebooklib.ITEM_IMAGE, ebooklib.ITEM_COVER)

templates_directory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")


def should_extract_item(item, extract_style):
    """Returns a boolean indicating if this item needs to be extracted

    :param item: EpubItem
    :type item: class:`ebook.epub.EpubItem`

    :param extract_style: Decides if CSS and Font items should be extracted
    :type extract_style: bool

    :returns: If the item should be extracted
    :rtype: bool
    """
    item_type = item.get_type()
    return ((item_type in IMAGE_TYPES) or
            (extract_style and item_type in STYLE_TYPES))


def get_filename(item, source_directory):
    """Returns the output file name of the item

    :param item: EpubItem
    :type item: class:`ebook.epub.EpubItem`

    :param source_directory: Source directory
    :type source_directory: str

    :returns: Output filename
    :rtype: str
    """
    item_type = item.get_type()
    if item_type in ((ebooklib.ITEM_DOCUMENT,) + (IMAGE_TYPES)):
        return os.path.join(source_directory, item.file_name)
    elif item_type in STYLE_TYPES:
        return os.path.join(source_directory, "_static", item.file_name)


def extract_item(item, source_directory, extract_style):
    """Extracts the Image, CSS or Font file

    :param item: EpubItem to extract
    :type item: class:`ebook.epub.EpubItem`

    :param source_directory: Source directory to extract the file to
    :type source_directory: str

    :param extract_style: Decides if CSS and Font items should be extracted
    :type extract_style: bool
    """
    if should_extract_item(item, extract_style):
        file_path = get_filename(item, source_directory)
        with open(file_path, 'wb') as ext_file:
            ext_file.write(item.content)


def generate_chapter(chapter_id, book, source_directory):
    """Generate ReST for each chapter

    :param chapter_id: ID of the chapter
    :type chapter_id: str

    :param book: Book instance
    :type book: class:`ebook.epub.EpubItem`

    :param source_directory: Source directory to extract the file to
    :type source_directory: str
    """
    chapter_item = book.epub.get_item_with_id(chapter_id[0])
    file_name = chapter_item.get_name()
    if file_name in book.subsections:
        chapter = Chapter(book, chapter_item)
        chapter.convert()
        for subchapter_href in book.subsections[file_name]:
            if subchapter_href != file_name:
                subchapter = Chapter(book, book.epub.get_item_with_href(subchapter_href))
                subchapter.convert()
                subchapter.write(source_directory)
                chapter.merge(subchapter)
        return chapter
    elif not any(file_name in subsections
                 for subsections in book.subsections.values()):
        chapter = Chapter(book, chapter_item)
        chapter.convert()
        return chapter


def merge_chapters(chapters):
    """Merge the unnamed chapters at the beginning and end of the book

    :param chapters: List of chapters
    :type chapters: list
    """
    def merge_range(start_index, end_index):
        """Merge the chapters present at the given range of indices (both inclusive)
        """
        for _ in range(start_index, end_index):
            chapters[start_index].merge(chapters[start_index+1])
            del chapters[start_index+1]

    if not chapters[0].title:
        current_chapter = 1
        while not chapters[current_chapter].title:
            current_chapter += 1
        merge_range(0, current_chapter-1)
        chapters[0].title = "Front Page"


def write_chapter(chapter, source_directory):
    """Write chapter to output file

    :param chapter: Chapter to write
    :type chapter: chapter

    :param source_directory: Source directory to extract the file to
    :type source_directory: str
    """
    chapter.write(source_directory)
    return chapter.file


class Converter:

    def __init__(self, file_name, output_directory, sphinx_theme_name, include_custom_css):
        self.book = Book(file_name)
        self.output_directory = output_directory
        self.source_directory = os.path.join(output_directory, 'source')
        self.theme = sphinx_theme_name
        self.include_custom_css = include_custom_css
        self.css_files = None

    def convert(self):
        # Create output directory structure
        click.echo("Creating directory structure")
        shutil.copytree(os.path.join(templates_directory, "makefiles"),
                        self.output_directory)
        directories = {os.path.dirname(get_filename(item, self.source_directory))
                       for item in self.book.epub.get_items()
                       if (should_extract_item(item, self.include_custom_css) or
                           item.get_type() == ebooklib.ITEM_DOCUMENT)}
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        self.css_files = [item.file_name for item in self.book.epub.get_items()
                          if item.get_type() == ebooklib.ITEM_STYLE]

        with ThreadPoolExecutor() as executor:
            # Generate ReST file for each chapter in ebook
            chapters = list(filter(None, tqdm(
                executor.map(lambda x: generate_chapter(x, self.book, self.source_directory),
                             self.book.epub.spine),
                total=len(self.book.epub.spine),
                desc="Generating ReST content",
                colour='Blue')))
            merge_chapters(chapters)
            self.book.toctree = list(tqdm(
                executor.map(lambda x: write_chapter(x, self.source_directory),
                             chapters),
                total=len(chapters),
                desc="Writing ReST files",
                colour='Blue'))
            # Extract other files from epub
            click.echo("Extracting images")
            list(executor.map(
                lambda x: extract_item(x, self.source_directory, self.include_custom_css),
                self.book.epub.get_items()))

        # Render jinja templates
        click.echo("Generating conf.py and index.rst")
        jinja_env = Environment(
            loader=PackageLoader("epub2sphinx")
        )
        with open(os.path.join(self.source_directory, 'conf.py'), 'x') as cf:
            if self.include_custom_css:
                cf.write(jinja_env.get_template('conf.py').render(book=self.book, theme=self.theme, css_files=self.css_files))
            else:
                cf.write(jinja_env.get_template('conf.py').render(book=self.book, theme=self.theme))
        with open(os.path.join(self.source_directory, 'index.rst'), 'x') as of:
            of.write(jinja_env.get_template('index.rst').render(book=self.book))
