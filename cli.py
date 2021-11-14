import click
import epub2sphinx
import subprocess
from epub2sphinx import constants
import os

def get_file_name(individual_file):
    if individual_file is not None:
        return individual_file.name

@click.command()
@click.option('-o','--output-directory',type=click.Path(),prompt=True,default=lambda : os.path.join(os.getcwd(),"output"),help=constants.cli_option_output_directory_help)
@click.option('-t','--theme','sphinx_theme_name',default="alabaster",type=str,prompt=True,help=constants.cli_option_theme_help)
@click.argument('input_file',type=click.File("r"))
@click.option('-b', '--build', 'post_conversion', flag_value='build', help=constants.cli_option_build_help)
@click.option('-s', '--serve', 'post_conversion', flag_value='serve', help=constants.cli_option_serve_help)
@click.option('-c', '--include-custom-css',is_flag=True, help=constants.cli_option_css_help)
@click.version_option(package_name='epub2sphinx')

def convert(output_directory,sphinx_theme_name,input_file, post_conversion,include_custom_css):
    '''\b
        This tool helps you to convert your epub files into sphinx format for a better reading experience.
        Kindly provide the epub file as the argument to this command.
    '''
    input_files= [input_file]
    with click.progressbar(input_files,label="converting to sphinx",item_show_func=get_file_name) as bar:
        for individual_file in bar:
            c = epub2sphinx.Converter(individual_file.name,output_directory,sphinx_theme_name.lower(),include_custom_css)
            c.convert()

    if post_conversion:
        # Build using Sphinx
        os.chdir(output_directory)
        build_exit_code = subprocess.call(["make html"], shell=True, stdout=subprocess.PIPE)
        html_path = os.path.join('build', 'html')
        if build_exit_code == 0 and os.path.isdir(html_path):
            if post_conversion == 'serve':
                # Serve on localhost
                os.chdir(html_path)
                subprocess.call(["python -m http.server --bind 127.0.0.1"], shell=True)
            else:
                click.echo("Build finished successfully")
        else:
            click.echo("Sphinx Build Failed: Something went wrong!")
