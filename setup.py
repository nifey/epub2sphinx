from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'epub2sphinx',
    version = '0.0.1',
    license = 'MIT',
    description = 'Tool to convert epub to ReST for Sphinx',
    url = 'https://github.com/nifey/epub2sphinx',
    py_modules = ['cli', 'epub2sphinx'],
    packages = find_packages(),
    install_requires = [requirements],
    entry_points = '''
        [console_scripts]
        epub2sphinx=cli:convert
    '''
)
