#!/usr/bin/env python
from flask import Flask
from flask_sillywalk import SwaggerApiRegistry, ApiParameter, ApiErrorResponse


app = Flask("foobar")

registry = SwaggerApiRegistry(app, baseurl="http://localhost:5000/api/v1")
register = registry.register
registerModel = registry.registerModel

@registerModel
class SomeCrazyClass(object):
    class HappyBirthdayException(Exception):
        pass
    def __init__(self, name, age, birthday="tomorrow"):
        self.name = name
        self.age = age
        self.birthday = birthday

    def say_happy_birthday(self):
        raise HappyBirthdayException("Chances are it's not your birthday.")


@register(
    "/api/v1/cheese/<cheeseName>",
    parameters=[
        ApiParameter(
            name="cheeseName",
            description="The name of the cheese to fetch",
            required=True,
            dataType="str",
            paramType="path",
            allowMultiple=False)
    ],
    errorResponses=[
        ApiErrorResponse(400, "Sorry, we're fresh out of that cheese."),
        ApiErrorResponse(418, "I'm actually a teapot")
    ])
def get_cheese(cheeseName):
  """Gets cheese, just like the name says."""
  return "Cheese {0}".format(cheeseName)

@register("/api/v1/holyHandGrenade/<number>")
def get_a_holy_hand_grenade(number):
  """Gets one or more holy hand grenades, just like the name says."""
  return "The holy hand grenade" * number

@register(
    "/api/v1/holyHandGrenade/<number>",
    method="PUT",
    parameters=[
        ApiParameter(
            name="number",
            description="The number of seconds to wait",
            required=True,
            dataType="int",
            paramType="path",
            allowMultiple=False),
        ApiParameter(
            name="target",
            description="At whom should I thrown the hand grenade?",
            required=False,
            dataType="str",
            paramType="query",
            allowMultiple=False),
    ])
def toss_the_grenade(number):
  """Toss the holy hand grenade after {number} seconds."""
  return "Waiting {0} seconds to toss the grenade.".format(number)

app.run(host="0.0.0.0", debug=True)
