import os
import pypandoc
import re

href_pattern = re.compile(r"(href=[\"\'][\w/.@-]*html)([#\'\"])")
svg_pattern = re.compile(r"\<svg[^\>]*\>(.*)\</svg\>", re.MULTILINE|re.DOTALL)
epub_metadata_pattern = re.compile(r"epub:[a-zA-Z]+=\"[^\"]*\"")

class Chapter:
    """This class represents an XHTML file in the epub's spine.

    :param chapter_item: EpubItem instance of the chapter
    :type chapter_item: class:`ebooklib.epub.EpubItem`

    :param title: Title of the chapter
    :type title: str

    :param file: XHTML filename of the chapter
    :type file: str

    :param content: XHTML or ReST content of the chapter
    :type content: str
    """
    def __init__(self, book, chapter_item):
        """Chapter Constructor

        :param epub: Book instance that contains the chapter
        :type epub: class:`epub2sphinx.Book`

        :param chapter_item: EpubItem of the chapter
        :type chapter_item: class:`ebooklib.epub.EpubItem`
        """
        self.chapter_item = chapter_item
        self.file = self.chapter_item.get_name()
        self.content = self.chapter_item.get_content().decode()
        if self.file in book.chapter_names.keys():
            self.title = book.chapter_names[self.file]
        elif self.content.find('epub:type="toc"') != -1:
            self.title = "Table of Contents"
        else:
            self.title = None

    def convert(self):
        """Convert the XHTML chapter content into ReST
        """
        html_content = re.sub(href_pattern, r"\1.html\2", self.content)
        html_content = re.sub(epub_metadata_pattern, "", html_content)
        if html_content.find("<svg") != -1:
            html_content = re.sub(svg_pattern, r"\1", html_content)
            html_content = html_content.replace("<image", "<img").replace("xlink:href", "src")
        self.content = pypandoc.convert_text(html_content, 'rst', format='html')

    def write(self, source_directory):
        """Write the ReST chapter content to output file

        :param source_directory: The source directory for writing the output file
        :type source_directory: str
        """
        with open(os.path.join(source_directory, self.file + '.rst'), 'x') as ch_file:
            # Add Chapter title
            if not self.title:
                self.title = "Unnamed chapter"
            ch_file.write('*'*len(self.title)+'\n')
            ch_file.write(self.title+'\n')
            ch_file.write('*'*len(self.title)+'\n')

            # Write ReST content
            ch_file.write(self.content)

    def merge(self, other_chapter):
        """Merges a chapter's content with this chapter

        :param other_chapter: The other chapter
        :type other_chapter: class:`Chapter`
        """
        self.content += other_chapter.content
        del other_chapter
