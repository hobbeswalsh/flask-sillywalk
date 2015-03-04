#!/usr/bin/env python
import os
import json
import unittest

from flask import Flask, make_response, request, Blueprint
from flask.ext.sillywalk import SwaggerApiRegistry, ApiParameter, ApiErrorResponse
from flask.ext.sillywalk.compat import s


class HappyBirthdayException(Exception):
    pass


class TestDecorators(unittest.TestCase):

    def _create_app(self):
        app = Flask("foobar")
        app.config['TESTING'] = True
        url = os.environ.get("URL", "localhost:5000")
        registry = SwaggerApiRegistry(app, baseurl="http://{0}/api/v1".format(url))

        @app.after_request
        def after_request(data):
            response = make_response(data)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers[
                'Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS , PUT'
            return response

        return app, registry

    def _create_blueprint(self, app):
        bp = Blueprint("blueish", "bluishns")
        app.register_blueprint(bp)
        return bp

    def _create_model(self, registerModel):
        @registerModel()
        class SomeCrazyClass(object):
            """This is just the most crazy class!"""

            def __init__(self, name, age, birthday="tomorrow"):
                self.name = name
                self.age = age
                self.birthday = birthday

            def say_happy_birthday(self):
                raise HappyBirthdayException("Chances are it's not your birthday.")

    def _create_add_register(self, add_register, app, bp=None):
        def get_cheese(cheeseName):
            """Gets cheese, just like the name says."""
            return json.dumps({"response": "OK", "message": "Sorry, we're fresh out of {0}!".format(cheeseName)})

        add_register(
            "/api/v1/cheese/<cheeseName>",
            get_cheese,
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
            ],
            bp=bp)
        # we have register our blueprint again to activate our added route
        if bp:
            app.register_blueprint(bp)

    def _create_register(self, register, app, bp=None):
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
            ],
            bp=bp)
        def get_cheese(cheeseName):
            """Gets cheese, just like the name says."""
            return json.dumps({"response": "OK", "message": "Sorry, we're fresh out of {0}!".format(cheeseName)})

        # XXX here we are not providing the basepath /api/v1
        @register(
            "/holyHandGrenade/<number>",
            method="GET",
            parameters=[
                ApiParameter(
                    name="number",
                    description="The number of hand grenades to get",
                    required=True,
                    dataType="int",
                    paramType="path",
                    allowMultiple=False)],
            bp=bp)
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
                    allowMultiple=False)],
            bp=bp)
        def toss_the_grenade(number):
            """Toss the holy hand grenade after {number} seconds."""
            target = request.args.get("target", "FOO")
            return json.dumps(
                "Waiting {0} seconds to toss the grenade at {1}.".format(
                    number,
                    target))

        # we have register our blueprint again to activate our added route
        if bp:
            app.register_blueprint(bp)

    def test_model(self):
        app, registry = self._create_app()
        self._create_model(registry.registerModel)
        ret = app.test_client().get("/api/v1/resources.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data['swaggerVersion'], '1.3')
        self.assertEqual(data['basePath'], 'http://localhost:5000/api/v1')
        self.assertEqual(data['apis'], [])
        self.assertEqual(data['apiVersion'], '1.0')
        self.assertEqual(data['models'], {'SomeCrazyClass': {
            'description': 'This is just the most crazy class!',
            'id': 'SomeCrazyClass',
            'required': ['name', 'age'], 'type': 'object',
            'properties': {'birthday': {'default': 'tomorrow'}}}})

    def test_register(self):
        app, registry = self._create_app()
        self._create_register(registry.register, app)
        ret = app.test_client().get("/api/v1/resources.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data['swaggerVersion'], '1.3')
        self.assertEqual(data['basePath'], 'http://localhost:5000/api/v1')
        self.assertEqual(sorted([x["path"] for x in data['apis']]),
                         ['/cheese.{format}', '/holyHandGrenade.{format}'])
        self.assertEqual(data['apiVersion'], '1.0')
        self.assertEqual(data['models'], {})
        # test cheese
        ret = app.test_client().get("/api/v1/cheese.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data["resourcePath"], "cheese")
        self.assertEqual([x.endpoint for x in app.url_map.iter_rules()],
                         ['holyHandGrenade',
                          'resources',
                          'cheese',
                          'get_a_holy_hand_grenade',
                          'toss_the_grenade',
                          'get_cheese',
                          'static'])
        self.assertEqual([x.rule for x in app.url_map.iter_rules()],
                         ['/api/v1/holyHandGrenade.json',
                          '/api/v1/resources.json', '/api/v1/cheese.json',
                          '/api/v1/holyHandGrenade/<number>',
                          '/api/v1/holyHandGrenade/<number>',
                          '/api/v1/cheese/<cheeseName>',
                          '/static/<path:filename>'])

    def test_add_register(self):
        app, registry = self._create_app()
        self._create_add_register(registry.add_register, app)
        ret = app.test_client().get("/api/v1/resources.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data['swaggerVersion'], '1.3')
        self.assertEqual(data['basePath'], 'http://localhost:5000/api/v1')
        self.assertEqual(sorted([x["path"] for x in data['apis']]),
                         ['/cheese.{format}'])
        self.assertEqual(data['apiVersion'], '1.0')
        self.assertEqual(data['models'], {})
        # test cheese
        ret = app.test_client().get("/api/v1/cheese.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data["resourcePath"], "cheese")

    def test_register_blueprint(self):
        app, registry = self._create_app()
        bp = self._create_blueprint(app)
        self._create_register(registry.register, app, bp)
        ret = app.test_client().get("/api/v1/resources.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data['swaggerVersion'], '1.3')
        self.assertEqual(data['basePath'], 'http://localhost:5000/api/v1')
        self.assertEqual(sorted([x["path"] for x in data['apis']]),
                         ['/cheese.{format}', '/holyHandGrenade.{format}'])
        self.assertEqual(data['apiVersion'], '1.0')
        self.assertEqual(data['models'], {})
        # test cheese
        ret = app.test_client().get("/api/v1/cheese.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data["resourcePath"], "cheese")
        # FIXME this is broken urls shouldn't be added multiple times
        self.assertEqual([x.endpoint for x in app.url_map.iter_rules()],
                         ['holyHandGrenade',
                          'resources',
                          'cheese',
                          'blueish.get_a_holy_hand_grenade',
                          'blueish.toss_the_grenade',
                          'blueish.get_cheese',
                          'static'])

    def test_add_register_blueprint(self):
        app, registry = self._create_app()
        bp = self._create_blueprint(app)
        self._create_add_register(registry.add_register, app, bp)
        ret = app.test_client().get("/api/v1/resources.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data['swaggerVersion'], '1.3')
        self.assertEqual(data['basePath'], 'http://localhost:5000/api/v1')
        self.assertEqual(sorted([x["path"] for x in data['apis']]),
                         ['/cheese.{format}'])
        self.assertEqual(data['apiVersion'], '1.0')
        self.assertEqual(data['models'], {})
        # test cheese
        ret = app.test_client().get("/api/v1/cheese.json")
        data = json.loads(s(ret.data))
        self.assertEqual(data["resourcePath"], "cheese")
        self.assertEqual([x.endpoint for x in app.url_map.iter_rules()],
                         ['resources',
                          'cheese',
                          'blueish.get_cheese',
                          'static'])
