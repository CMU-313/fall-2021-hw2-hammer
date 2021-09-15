from fabric.api import env, task
from fabric.colors import green

from ..conf import setup_environment
from ..literals import DB_MYSQL
import mysql


@task
def create_database():
    """
    Create the Mayan EDMS database
    """
    setup_environment()
    print(green('Creating Mayan EDMS database', bold=True))
    
    if env.database_manager == DB_MYSQL:
        mysql.create_database()


@task
def create_user():
    """
    Create the Mayan EDMS user
    """
    setup_environment()
    print(green('Creating Mayan EDMS user', bold=True))
    
    if env.database_manager == DB_MYSQL:
        mysql.create_user()


@task
def drop_database():
    """
    Drop Mayan EDMS's database
    """
    setup_environment()
    print(green('Droping Mayan EDMS database', bold=True))

    if env.database_manager == DB_MYSQL:
        mysql.drop_database()


@task
def drop_user():
    """
    Drop Mayan EDMS's user
    """
    setup_environment()
    print(green('Droping Mayan EDMS user', bold=True))

    if env.database_manager == DB_MYSQL:
        mysql.drop_user()
