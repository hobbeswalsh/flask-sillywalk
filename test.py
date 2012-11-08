#!/usr/bin/python

from flask import Flask
from flask_swagger import SwaggerApiRegistry


app = Flask("foobar")

registry = SwaggerApiRegistry(app, basepath="/api/v1")
register = registry.register

@register("/api/v1/wordList/<listName>")
def do_a_foobar(listName):
  return "FOO BAR {0}".format(listName)

app.run(debug=True)
