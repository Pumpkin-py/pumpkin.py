import os
import importlib
import logging
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger("pumpkin")


class Database:
    def __init__(self):
        self.base = declarative_base()
        self.db = create_engine(
            os.getenv("DB_STRING"),
            # This forces the SQLAlchemy 1.4 to use the 2.0 syntax
            future=True,
        )


database = Database()
session = sessionmaker(database.db)()


def _list_directory_directories(directory: str) -> List[str]:
    """Return filtered list of directories.

    :param directory: Absolute or relative (from the __main__ file) path to the
        directory.
    :returns: List of paths to directories inside the requested directory.
        Directories starting with underscore (e.g. __pycache__) are not
        included.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"{directory} is not a directory.")

    all_files = os.listdir(directory)
    filenames = [f for f in all_files if not f.startswith("_")]
    files = [os.path.join(directory, d) for d in filenames]
    return [d for d in files if os.path.isdir(d)]


def _import_database_tables():
    """Import database tables from the "modules/" directory."""
    repositories: List[str] = _list_directory_directories("modules")
    for repository in repositories:
        modules: List[str] = _list_directory_directories(repository)
        for module in modules:
            # Detect module's database files
            # TODO This has not been tested with "database/" as directory.
            # 1/ Do we need that functionality?
            # 2/ Do we want to support this? It may be solved just by importing the modules
            #    to the "database/__init__.py" file.
            database_stub: str = os.path.join(module, "database")
            if not os.path.isfile(database_stub + ".py") and not os.path.isdir(database_stub):
                continue

            # Import the module
            try:
                import_stub: str = database_stub.replace("/", ".")
                importlib.import_module(import_stub)
                logger.debug(f"Imported database models in {import_stub}.")
            except ModuleNotFoundError as exc:
                # TODO How to properly log errors?
                logger.error(f"Could not import database models in {import_stub}: {exc}.")


def init_core():
    """Load core models and create their tables."""
    # Import core tables
    importlib.import_module("database.config")

    database.base.metadata.create_all(database.db)
    session.commit()


def init_modules():
    """Load all database models and create their tables."""
    # Find and import module tables
    _import_database_tables()

    database.base.metadata.create_all(database.db)
    session.commit()
