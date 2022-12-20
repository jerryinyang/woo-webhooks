from app import db, User, Log
import click
from flask.cli import with_appcontext

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()