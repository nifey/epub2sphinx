import click
import epub2sphinx
from epub2sphinx import constants
import os

def get_file_name(individual_file):
    if individual_file is not None:
        return individual_file.name

@click.command()
@click.option('-o','--output-directory',type=click.Path(),prompt=True,default=lambda : os.path.join(os.getcwd(),"output"),help=constants.cli_option_output_directory_help)
@click.option('-t','--theme','sphinx_theme_name',default="alabaster",type=str,prompt=True,help=constants.cli_option_theme_help)
@click.version_option()
@click.argument('input_file',type=click.File("r"))
@click.option('-s', '--serve', prompt=True, type=bool, default='n', help="Serve the file on localhost")

def convert(output_directory,sphinx_theme_name,input_file, serve):
    '''\b
        This tool helps you to convert your epub files into sphinx format for a better reading experience.
        Kindly provide the epub file as the argument to this command.
    '''
    input_files= [input_file]
    with click.progressbar(input_files,label="converting to sphinx",item_show_func=get_file_name) as bar:
        for individual_file in bar:
            c = epub2sphinx.Converter(individual_file.name,output_directory,sphinx_theme_name.lower(), serve)
            c.convert()
