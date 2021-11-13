import click
import epub2sphinx

@click.command()
@click.option('-o','--output-directory',type=click.Path(),default='.',help="The name of the output directory where the ReST file will be generated.")
@click.option('-t','--theme','sphinx_theme_name',default="Alabaster",prompt=True,help="The name of the sphinx theme. You can check for the available themes at https://sphinx-themes.org/#themes")
@click.version_option()
@click.argument('input_file',type=click.File("r"))
def convert(output_directory,sphinx_theme_name,input_file):
    ''' This tool helps you to convert your epub files into sphinx format for a better reading experience.
        Kindly provide the epub file as the argument to this command.'''
    epub2sphinx.convert_epub(input_file.name,output_directory,sphinx_theme_name)
