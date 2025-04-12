import click, csv
from flask import Flask
from flask.cli import with_appcontext
from App import app, initialize_db


@app.cli.command("init")
def initialize():
  initialize_db()
