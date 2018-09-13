from flask import render_template, session, redirect, url_for, current_app
from .. import db
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
