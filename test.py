#!/usr/bin/python

from flask import Flask
from flask_swagger import SwaggerApiRegistry


app = Flask("foobar")

registry = SwaggerApiRegistry(app, baseurl="http://localhost:5000/api/v1")
register = registry.register

@register("/api/v1/wordList/<listName>")
def do_a_foobar(listName):
  """Does a foobar, just like the name says."""
  return "FOO BAR {0}".format(listName)

@register("/api/v1/wordList/<listName>", method="PUT")
def do_a_barfoo(listName):
  """Does a barfoo, just like the name says."""
  return "BAR FOO {0}".format(listName)


app.run(debug=True)
