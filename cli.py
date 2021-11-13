import click
import epub2sphinx
import os

def get_file_name(individual_file):
    if individual_file is not None:
        return individual_file.name

@click.command()
@click.option('-o','--output-directory',type=click.Path(),prompt=True,default=lambda : os.path.join(os.getcwd(),"output"),help="The name of the output directory where the ReST file will be generated. Kindly make sure that the given directory is not existing already.")
@click.option('-t','--theme','sphinx_theme_name',default="alabaster",type=str,prompt=True,help="The name of the sphinx theme. You can check for the available themes at https://sphinx-themes.org/#themes")
@click.version_option()
@click.argument('input_file',type=click.File("r"))
def convert(output_directory,sphinx_theme_name,input_file):
    ''' This tool helps you to convert your epub files into sphinx format for a better reading experience.
        Kindly provide the epub file as the argument to this command.'''
    input_files= [input_file]
    with click.progressbar(input_files,label="converting to sphinx",item_show_func=get_file_name) as bar:
        for individual_file in bar:
            epub2sphinx.convert_epub(individual_file.name,output_directory,sphinx_theme_name.lower())
