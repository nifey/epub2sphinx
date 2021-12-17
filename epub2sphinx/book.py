import datetime
import ebooklib
import re

from ebooklib import epub

def escape_quotes(text):
    """Function to escape any ' or " symbols present in the string

    :param text: Input string
    :param type: str

    :returns: Escaped string
    :rtype: str
    """
    if text is not None:
        return text.replace("'","\\'").replace('"','\\"')

def get_chapter_names_and_subsections(epub):
    """Extracts the chapter names from the title
    Also returns the subsections information

    :param epub: EpubBook instance
    :param type: class:`ebooklib.epub.EpubBook`

    :returns: (File name => Chapter Name) and (File => Subsection file) mappings
    :rtype: (dict, dict)
    """
    chapter_names = {}
    href_pattern = re.compile(r"([\w/.@-]*html)#?[^\'\"]*")
    def get_names_and_subsections(item):
        """Fill the chapter_names dict with the file -> title mapping.
        Returns a list of files that are part of this section.
        """
        subsections = []
        if isinstance(item, ebooklib.epub.Link):
            file_name = re.sub(href_pattern, r"\1", item.href)
            if file_name not in chapter_names:
                chapter_names[file_name] = item.title
            subsections.append(file_name)
        elif isinstance(item, tuple) and isinstance(item[0], ebooklib.epub.Section):
            file_name = re.sub(href_pattern, r"\1", item[0].href)
            if file_name not in chapter_names:
                chapter_names[file_name] = item[0].title
            subsections.append(file_name)
            for sub_item in item[1]:
                subsubsections = get_names_and_subsections(sub_item)
                if isinstance(subsubsections, list):
                    subsections.append(*subsubsections)
                else:
                    subsections.append(subsubsections)
        return subsections
    sections = {files[0]:files[1:]
                for files in [get_names_and_subsections(item)
                              for item in epub.toc]}
    return chapter_names, sections

class Book:
    """This class represents an epub book.

    :param epub: EpubBook instance of the file
    :type epub: class:`ebooklib.epub.EpubBook`

    :param title: Title of the book
    :type title: str

    :param chapter_names: (File name => Chapter name) Mapping
    :type chapter_names: dict

    :param toctree: List of filenames to be added to toctree
    :type toctree: list

    :param author: Book Author name
    :type author: str

    :param rights: Book Copyright or License details
    :type rights: str
    """
    def __init__(self, file_name):
        """Book Constructor

        :param file_name: Name of the epub file
        :type file_name: str
        """
        self.epub = epub.read_epub(file_name)
        self.title = escape_quotes(self.epub.title)
        self.chapter_names, self.subsections = get_chapter_names_and_subsections(self.epub)
        self.toctree = []
        try:
            self.author = escape_quotes(self.epub.get_metadata('DC', 'creator')[0][0])
        except:
            self.author = None
        try:
            self.rights = escape_quotes(self.epub.get_metadata('DC', 'rights')[0][0])
        except:
            if self.author:
                self.rights = datetime.datetime.now().strftime("%Y") + " " + self.author
            else:
                self.rights = None
