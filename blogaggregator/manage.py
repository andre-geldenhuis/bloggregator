#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import MigrateCommand

from blogaggregator.app import create_app
from blogaggregator.user.models import User
from blogaggregator.settings import DevConfig, ProdConfig
from blogaggregator.database import db
from waitress import serve

if os.environ.get("BLOGAGGREGATOR_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

manager = Manager(app)
TEST_CMD = "py.test tests"

def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}

@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main(['tests', '--verbose'])
    return exit_code

@manager.command
def runwaitress():
    serve(app,host="0.0.0.0", port=5000)


@manager.command
def cmdline():
    """
    A small function  to allow testting the sqalchemy phrasing in ipython
    functions similarly to a view
    """
    from flask import Blueprint, render_template, request, flash, redirect, url_for, session
    from flask.ext.login import login_required
    from flask.ext.login import current_user
    from blogaggregator.user.forms import User
    from blogaggregator.user.models import User
    from blogaggregator.user.models import Post
    from sqlalchemy import desc

    1/0


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manager.run()
