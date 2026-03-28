import click

@click.group()
def cli():
    """DataHub CLI"""
    pass

@cli.command()
def push():
    """Pushes local commits to the server over HTTP."""
    click.echo("Pushing data...")

if __name__ == '__main__':
    cli()
