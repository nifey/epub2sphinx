from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name = 'epub2sphinx',
    version = '0.0.1',
    license = 'MIT',
    description = 'Tool to convert epub to ReST for Sphinx',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/nifey/epub2sphinx',
    project_urls={
        "Bug Tracker": "https://github.com/nifey/epub2sphinx/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Topic :: Documentation :: Sphinx",
    ],
    py_modules = ['cli', 'epub2sphinx'],
    packages = find_packages(),
    package_data={'epub2sphinx': ['templates/*']},
    install_requires = [requirements],
    entry_points = '''
        [console_scripts]
        epub2sphinx=cli:convert
    '''
)
