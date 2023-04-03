# epub2sphinx

epub2sphinx is a tool to convert epub files directly into HTML sites using [Pandoc](https://pandoc.org/) and [Sphinx](https://www.sphinx-doc.org/).
It can use any of pre-existing Sphinx themes (like [these](https://sphinx-themes.org/)) for the generated HTML site.

It uses Pandoc for converting HTML data inside epub files into ReST files and then uses Sphinx to convert them into a HTML site.

It creates a directory structure similar to what `sphinx-quickstart` generates by default.

Built during [FOSSHack 21](https://fossunited.org/fosshack/2021) to solve [this issue](https://github.com/kaniyamfoundation/projectideas/issues/70).

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
  pip install epub2sphinx
  ```

## Usage
```
Usage: epub2sphinx <epub_file_name> [-o <output_directory_path>] [-t <sphinx_theme_name>] [-b,--build|-B,--no-build] [-s|--serve] [-c] [-p <port_number>]

  This tool helps you to convert your epub files into sphinx format for a better reading experience.
  Kindly provide the epub file as the argument to this command.

Options:
  -o, --output-directory PATH   The name of the output directory where the ReST file will be generated.
                                Kindly make sure that the given directory is not existing already.
  -t, --theme TEXT              The name of the sphinx theme.You can check for the available themes at:
                                <https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes>
  -b, --build / -B, --no-build  Build HTML from the generated ReST files using Sphinx.
                                Sphinx has to be installed for this to work.  [default: b]
  -s, --serve                   Build HTML using Sphinx and Serve the files on localhost.
                                Sphinx has to be installed for this to work.
  -c, --include-custom-css      Include the custom CSS and Fonts from the EPUB for the HTML output
  --overwrite                   Overwrite the output directory if present already
  -p, --port INTEGER            The port number on which the files will be served after conversion
  --version                     Show the version and exit.
  --help                        Show this message and exit.
```
### Example
```
epub2sphinx -o out_dir -t classic my_book.epub

# To generate HTML files using Sphinx
cd out_dir
make html
```

## Usecase

epub2sphinx can be used to convert public domain or CC-licensed epub files into static web pages that allows people to read them online.
This will be useful for sites like [Project Gutenberg](https://www.gutenberg.org) or [FreeTamilEbooks](https://freetamilebooks.com/).
Eventhough Project Gutenberg has an option to read online, it is very plain.
Using Sphinx allows us to make use of any [default](https://www.sphinx-doc.org/en/master/usage/theming.html#builtin-themes) or [custom](https://sphinx-themes.org/) sphinx theme to make it look better.

## Screenshots of comparison

[Project Gutenberg online read](https://www.gutenberg.org/cache/epub/98/pg98-images.html#link2H_4_0002) vs Sphinx generated output

![image](https://user-images.githubusercontent.com/24192122/141684781-d7259e32-9055-4f68-9d0c-32475d350f8d.png)

![image](https://user-images.githubusercontent.com/24192122/141684776-4a1e5012-7d11-4f82-a25b-2cfe8374ae87.png)

## Contributing

Contributions are welcome.
Fork the repo and Create a PR with your changes.
If you are working on any of the existing issues, please add a comment on the issue to avoid duplicated effort.

![GitHub](https://img.shields.io/github/license/nifey/epub2sphinx)
![GitHub issues](https://img.shields.io/github/issues/nifey/epub2sphinx)
![GitHub forks](https://img.shields.io/github/forks/nifey/epub2sphinx?style=social)
![GitHub Repo stars](https://img.shields.io/github/stars/nifey/epub2sphinx?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/nifey/epub2sphinx?style=social)
