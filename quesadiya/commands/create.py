import click

from quesadiya.db.schema import ProjectStatusEnum
from quesadiya.db import factory

from quesadiya import utils
import quesadiya

import os


# TODO: replace AssertionError with custom exception class
# TODO: add function to print common error message
def operator(
    project_name,
    project_description,
    admin_name,
    admin_password,
    input_data_path,
    admin_contact
):
    if input_data_path[-6:] != ".jsonl":
        raise ValueError(
            "The extension of `DATAPATH` must be jsonl (jsonlines file), "
            "instead received {}".format(input_data_path)
        )
    admin_interface = factory.get_admindb_interface()
    # create folder for project inside `projects` dir and insert project.db in it
    project_dir = os.path.join(quesadiya.get_projects_path(), project_name)
    # TODO: create a custom exception
    if admin_interface.check_project_exists(project_name):
        raise AssertionError(
            "Project ({}) already exists. If you'd like to add new data, "
            "run `quesadiya modify --add-data`.".format(project_name)
        )
    try:
        os.mkdir(project_dir)
    except PermissionError:
        raise PermissionError(
            "Permission is denied to create a project folder under {}. "
            "Make sure you have the right permission to create folder under "
            "the directory.".format(quesadiya.get_projects_path())
        )
    # create project.db
    factory.init_projectdb(project_dir)
    # get interface
    projectdb_interface = factory.get_projectdb_interface(project_dir)
    # load data and format it to be inserted into project.db
    triplets, candidates, sample_text = \
        utils.format_input(input_data_path)
    # start inserting rows into tables in project.db
    click.echo("Inserting data into {} space. This may take a while...".format(project_name))
    projectdb_interface.triplets_bulk_insert(triplets)
    projectdb_interface.candidate_groups_bulk_insert(candidates)
    projectdb_interface.sample_text_bulk_insert(sample_text)
    # insert project into admin.db
    admin_interface.insert_project(
        project_name=project_name,
        project_description=project_description,
        admin_name=admin_name,
        admin_password=admin_password,
        admin_contact=admin_contact,
        status=ProjectStatusEnum.not_running
    )
    # insert bulk data into database
    click.echo('Finish creating {}'.format(project_name))
