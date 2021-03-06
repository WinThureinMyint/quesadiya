import pytest

import os
import subprocess
import sqlite3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    PrimaryKeyConstraint
)
from sqlalchemy.ext.declarative.api import DeclarativeMeta


class TestFileOps:
    """Test file operations in `setup.py`"""

    # ../quesadiya/test
    root_dir = os.path.dirname(os.path.abspath(__file__))

    def test_version_check(self):
        """Check the version of sqlite3."""
        # sqlite3 v-4. is not released yet (9/13/2020)
        assert sqlite3.sqlite_version_info > (2, 40)
        assert sqlite3.sqlite_version_info > (3, 3)
        assert sqlite3.sqlite_version_info < (4, 1)

    def test_mkdir(self):
        """Test mkdir to create `projects` folder under the root directory of
        this package.
        """
        # create a directory named projects
        dir_path = os.path.join(self.root_dir, "projects")
        assert not os.path.exists(dir_path)
        if not os.path.exists(dir_path):
            try:
                os.mkdir(dir_path)
            except PermissionError:
                raise PermissionError(
                    "permission is denied to create a project folder under {}. "
                    "make sure you have the right permission to create folder, or "
                    "try `pip install --user quesadiya` or "
                    "`python setup.py install --user`".format(base_dir)
                )
        # make sure the path exists
        assert os.path.exists(dir_path)
        # remove the directory
        os.rmdir(dir_path)


class TestSQLQuery:
    """Test sql queries in `setup.py`"""

    Base = declarative_base()

    class Projects(Base):
        """Table schema for `projects` table in `admin.db`."""
        __tablename__ = "projects"
        project_id = Column(Integer, index=True, primary_key=True)
        project_name = Column(String(30), nullable=False)
        owner_name = Column(String(30), nullable=False)
        owner_password = Column(String(30), nullable=False)
        date_created = Column(Date(), nullable=False)


    class Collaborators(Base):
        """Table schema for `collaborators` table in `admin.db`."""
        __tablename__ = "collaborators"
        # set foregin key to projects table
        project_id =  Column(
            Integer, ForeignKey("projects.project_id"), nullable=False
        )
        collaborator_name = Column(String(30), nullable=False)
        collaborator_password = Column(String(30), nullable=False)
        # set project_id and collaborator_name primary key
        __table_args__ = (
            PrimaryKeyConstraint('project_id', 'collaborator_name'),
            {}
        )

    # ../quesadiya/test
    root_dir = os.path.dirname(os.path.abspath(__file__))

    def test_create_db_in_root(self):
        """Create db file under the root directory of this package."""
        # make sure db file exists
        db_uri = 'sqlite:///' + os.path.join(self.root_dir, "test.db")
        engine = create_engine(db_uri, echo=True, encoding="utf-8")
        self.Base.metadata.create_all(engine)
        assert os.path.exists(os.path.join(self.root_dir, "test.db"))
        os.remove(os.path.join(self.root_dir, "test.db"))

    def test_create_table(self):
        """Create table in test database file."""
        # query to create projects table
        db_uri = 'sqlite:///' + os.path.join(self.root_dir, "test.db")
        engine = create_engine(db_uri, echo=True, encoding="utf-8")
        self.Base.metadata.create_all(engine)
        # get all tables in test.db and make sure names are correct
        engine = create_engine(db_uri, echo=True, encoding="utf-8")
        # print(engine.table_names())
        count = 0
        expected = set(['projects', 'collaborators'])
        assert set(engine.table_names()) == expected
        os.remove(os.path.join(self.root_dir, "test.db"))
