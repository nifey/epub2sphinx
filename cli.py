import click
import epub2sphinx
import os
import shutil
import socket
import subprocess
import time
import tempfile
from contextlib import closing
from epub2sphinx import constants


@click.command()
@click.option('-o', '--output-directory', type=click.Path(), help=constants.cli_option_output_directory_help)
@click.option('-t', '--theme', 'sphinx_theme_name', default="alabaster", type=str, prompt=True,
              help=constants.cli_option_theme_help)
@click.argument('input_file', type=click.File("r"))
@click.option('-b/-B', '--build/--no-build', 'build', is_flag=True, default=True, help=constants.cli_option_build_help, show_default=True)
@click.option('-s', '--serve', 'serve', is_flag=True, help=constants.cli_option_serve_help)
@click.option('-c', '--include-custom-css', is_flag=True, help=constants.cli_option_css_help)
@click.option('--overwrite', is_flag=True, help=constants.cli_option_overwrite_help)
@click.option('-p', '--port', type=int, default=0, help=constants.cli_option_port_help)
@click.version_option(package_name='epub2sphinx')
def convert(output_directory, sphinx_theme_name, input_file, build, serve, include_custom_css, overwrite, port):
    '''\b
        This tool helps you to convert your epub files into sphinx format for a better reading experience.
        Kindly provide the epub file as the argument to this command.
    '''
    if port:
        is_port_available = check_port_availability("127.0.0.1", port)
        if not is_port_available:
            click.echo(f"Port {port} is already in use. Aborting!")
            exit(1)

    output_directory = output_directory or default_output_directory(input_file.name)
    output_directory = os.path.abspath(output_directory)
    click.echo("Writing output to {}".format(output_directory))

    if os.path.isdir(output_directory):
        if overwrite or click.confirm("{} already exists, Do you want to overwrite it?".format(output_directory)):
            shutil.rmtree(output_directory)
        else:
            click.echo("Aborting")
            exit(1)

    temp_directory = tempfile.TemporaryDirectory()
    build_directory = os.path.join(temp_directory.name, "output")
    start_time = time.time()
    c = epub2sphinx.Converter(input_file.name, build_directory, sphinx_theme_name.lower(), include_custom_css)
    c.convert()
    click.echo("Conversion finished in {:.2f}s".format(time.time() - start_time))

    if build:
        # Build using Sphinx
        os.chdir(build_directory)
        build_exit_code = subprocess.call(["make html"], shell=True, stdout=subprocess.PIPE)
        html_path = os.path.join('build', 'html')
        if build_exit_code == 0 and os.path.isdir(html_path):
            shutil.copytree(html_path, output_directory)
            if serve:
                # Serve on localhost
                os.chdir(output_directory)
                # 0 will automatically make use of the next available port
                subprocess.call([f"python -m http.server {port} --bind 127.0.0.1"], shell=True)
            else:
                click.echo("Build finished successfully")
        else:
            click.echo("Sphinx Build Failed: Something went wrong!")
    else:
        shutil.copytree(build_directory, output_directory)
    temp_directory.cleanup()


def check_port_availability(host: str, port: int):
    """
    Check if the port provided by the user is available to serve.

    :param host: 127.0.0.1
    :param port: 8000
    :return: Bool
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) != 0


def default_output_directory(file_name: str) -> str:
    """
    Generate the default output directory path from the given file name in the current working directory.

    :param str file_name: The name of the input (EPUB) file
    :return: the path where the ReST/HTML files should be placed
    :rtype: str
    """
    output_name = file_name.split(os.path.sep)[-1]
    output_name = output_name.removesuffix('.epub')
    return os.path.join(os.getcwd(), output_name)
