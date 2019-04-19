import os
import psycopg2
from psycopg2.extras import DictCursor

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        # open a connection, save it to close when done
        DB_URL = os.environ.get('DATABASE_URL', None)
        if DB_URL:
            g.db = psycopg2.connect(DB_URL, sslmode='require')
        else:
            g.db = psycopg2.connect(
                dbname=current_app.config['DB_NAME'],
                user=current_app.config['DB_USER'],
                cursor_factory=DictCursor
            )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close() # close the connection


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        cur = db.cursor()
        cur.execute(f.read())
        cur.close()
        db.commit()

def add_user():
    db = get_db()
    cur = db.cursor()
    user_email = input("User Email: ")
    user_password = input("User Password: ")
    user_role= input("User Role (student/teacher): ")
    user_first = input("First Name: ")
    user_last = input("Last Name: ")
    cur.execute("INSERT INTO users (email, password, role, first_name, last_name) VALUES(%s, %s, %s, %s, %s)", (user_email, user_password, user_role, user_first, user_last))
    db.commit()
    cur.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('add-user')
@with_appcontext
def add_user_command():
    """Create new user"""
    add_user()
    click.echo('Created user.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_user_command)
