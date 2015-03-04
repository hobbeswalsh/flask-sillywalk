#!/usr/bin/env python
import os
import json

from flask import Flask, make_response, request
from flask.ext.sillywalk import SwaggerApiRegistry, ApiParameter, ApiErrorResponse


app = Flask("foobar")

url = os.environ.get("URL", "localhost:5000")
registry = SwaggerApiRegistry(app, baseurl="http://{0}/api/v1".format(url))
register = registry.register
registerModel = registry.registerModel


class HappyBirthdayException(Exception):
    pass


@registerModel()
class SomeCrazyClass(object):
    """This is just the most crazy class!"""

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
            allowMultiple=False)],
    notes='For getting cheese, you know...',
    responseMessages=[
        ApiErrorResponse(400, "Sorry, we're fresh out of that cheese."),
        ApiErrorResponse(418, "I'm actually a teapot")
    ])
def get_cheese(cheeseName):
    """Gets cheese, just like the name says."""
    return json.dumps(
        {"response": "OK", "message": "Sorry, we're fresh out of {0}!".format(
            cheeseName)
        })


@register(
    "/api/v1/holyHandGrenade/<number>",
    method="GET",
    parameters=[
        ApiParameter(
            name="number",
            description="The number of hand grenades to get",
            required=True,
            dataType="int",
            paramType="path",
            allowMultiple=False)])
def get_a_holy_hand_grenade(number):
    """Gets one or more holy hand grenades, just like the name says."""
    return json.dumps("Fetching {0} holy hand grenades".format(number))


@register(
    "/api/v1/holyHandGrenade/<number>",
    method="POST",
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
            allowMultiple=False)])
def toss_the_grenade(number):
    """Toss the holy hand grenade after {number} seconds."""
    target = request.args.get("target", "FOO")
    return json.dumps(
        "Waiting {0} seconds to toss the grenade at {1}.".format(
            number,
            target))


@app.after_request
def after_request(data):
    response = make_response(data)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers[
        'Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS , PUT'
    return response


port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)
