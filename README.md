# epub2sphinx

epub2sphinx is a tool to convert epub files to ReST for [Sphinx](https://www.sphinx-doc.org/).

It uses [Pandoc](https://pandoc.org/) for converting HTML data inside epub files into ReST.

It creates a directory structure similar to what `sphinx-quickstart` generates by default.

## Installation
- Install pandoc
  ```bash
  # On Ubuntu
  sudo apt-get install pandoc
  # On Arch Linux
  pacman -S pandoc
  ```
  For installing on other platforms, look [here](https://pandoc.org/installing.html).

- Install epub2sphinx
  ```bash
  python setup.py install
  ```

- Install Sphinx

  epub2sphinx can generate ReST files without Sphinx, but Sphinx is used to build the HTML files if --build or --serve flags are used.
  ```bash
  pip3 install sphinx
  ```

## Usage
```
Usage: epub2sphinx [-o <output_directory_path>] [-t <sphinx_theme_name>] [-s|--server|-b|--build] [-c] <epub_file_name>

  This tool helps you to convert your epub files into sphinx format for a better reading experience.
  Kindly provide the epub file as the argument to this command.

Options:
  -o, --output-directory PATH  The name of the output directory where the ReST file will be generated.
                               Kindly make sure that the given directory is not existing already.
  -t, --theme TEXT             The name of the sphinx theme.You can check for the available themes at:
                               <https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes>
  -b, --build                  Build HTML from the generated ReST files using Sphinx.
                               Sphinx has to be installed for this to work.
  -s, --serve                  Build HTML using Sphinx and Serve the files on localhost.
                               Sphinx has to be installed for this to work.
  -c, --include-custom-css     Include the custom CSS from the EPUB for the HTML output
  --version                    Show the version and exit.
  --help                       Show this message and exit.
```
### Example
```
epub2sphinx -o out_dir -t classic my_book.epub

# To generate HTML files using Sphinx
cd out_dir
make html
```

## Screenshots of comparison

[Project Gutenberg online read](https://www.gutenberg.org/cache/epub/98/pg98-images.html#link2H_4_0002) vs Sphinx generated output

![image](https://user-images.githubusercontent.com/24192122/141684781-d7259e32-9055-4f68-9d0c-32475d350f8d.png)

![image](https://user-images.githubusercontent.com/24192122/141684776-4a1e5012-7d11-4f82-a25b-2cfe8374ae87.png)

## Usecase

epub2sphinx can be used to convert public domain or CC-licensed epub files into static web pages that allows people to read them online.
This will be useful for sites like [Project Gutenberg](https://www.gutenberg.org) or [FreeTamilEbooks](https://freetamilebooks.com/).
Eventhough Project Gutenberg has an option to read online, it is very plain.
Using Sphinx allows us to make use of any [default](https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes) or [custom](https://sphinx-themes.org/) sphinx theme to make it look better.


![GitHub](https://img.shields.io/github/license/nifey/epub2sphinx)
![GitHub issues](https://img.shields.io/github/issues/nifey/epub2sphinx)
![GitHub forks](https://img.shields.io/github/forks/nifey/epub2sphinx?style=social)
![GitHub Repo stars](https://img.shields.io/github/stars/nifey/epub2sphinx?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/nifey/epub2sphinx?style=social)
