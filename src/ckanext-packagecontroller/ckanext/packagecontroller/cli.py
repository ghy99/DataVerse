import click


@click.group(short_help="packagecontroller CLI.")
def packagecontroller():
    """packagecontroller CLI.
    """
    pass


@packagecontroller.command()
@click.argument("name", default="packagecontroller")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [packagecontroller]
