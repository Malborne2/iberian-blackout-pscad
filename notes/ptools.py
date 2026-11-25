"""Shared helpers for driving PSCAD through the COM API.

Golden rule encoded here: never edit the .pscx while the project is loaded.
"""
import os
import time
import mhi.pscad as p

PROJECT = 'Spanish_grid_model'
FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    PROJECT + '.pscx')


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def names(app):
    return [x['name'] for x in app.projects()]


def ensure_loaded(name=PROJECT):
    app = p.connect()
    if name not in names(app):
        log('loading', name)
        app.load(FILE)
    return app, app.project(name)


def save_unload():
    app = p.connect()
    pr = app.project(PROJECT)
    pr.save()
    pr.unload()
    log('saved + unloaded')
