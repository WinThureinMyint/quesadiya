import click

import os

import quesadiya
import quesadiya.commands.create
import quesadiya.commands.run
import quesadiya.commands.inspect
import quesadiya.commands.delete
import quesadiya.commands.export
import quesadiya.commands.modify


@click.group()
@click.version_option()
def cli():
    """Delicious mexican pizza."""
    pass


@cli.command()
def path():
    """print path to this package."""
    click.echo("quesadiya resides in {}".format(
        quesadiya.get_base_path()
    ))


@cli.command()
@click.argument(
    "project_name",
    metavar="PROJECT"
)
@click.argument("admin_name")
@click.argument(
    "admin_password",
    metavar="PASSWORD"
)
def create(project_name, admin_name, admin_password):
    """create annotation project."""
    quesadiya.commands.create.operator(
        project_name=project_name,
        admin_name=admin_name,
        admin_password=admin_password
    )


@cli.command()
@click.argument(
    "project_name",
    metavar="PROJECT"
)
def run(project_name):
    """run annotation project indicated by project name."""
    quesadiya.commands.run.operator(project_name=project_name)


@cli.command()
@click.argument(
    "project_name",
    metavar="PROJECT"
)
def inspect(project_name):
    """show project information indicated by project name."""
    quesadiya.commands.inspect.operator(project_name=project_name)


@cli.command()
@click.argument(
    "project_name",
    metavar="PROJECT"
)
def modify(project_name):
    """modify project indicated by project name."""
    quesadiya.commands.modify.operator(project_name=project_name)


@cli.command()
@click.argument(
    "project_name",
    metavar="PROJECT"
)
def delete(project_name):
    """delete project indicated by project name."""
    quesadiya.commands.delete.operator(project_name=project_name)


@cli.command()
@click.argument(
    "project_name",
    metavar="PROJECT"
)
def export(project_name):
    """export data associated with project indicated by project name."""
    quesadiya.commands.export.operator(project_name=project_name)
