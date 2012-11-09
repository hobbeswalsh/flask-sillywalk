flask-sillywalk
===============

A Flask extension that implements Swagger support (http://swagger.wordnik.com/)

What's Swagger?
---------------

Swagger is a spec to help you document your APIs. It's flexible and
produces beautiful API documentation that can then be used to build
API-explorer-type sites, much like the one at
http://developer.wordnik.com/docs -- To read more about the Swagger
spec, head over to https://github.com/wordnik/swagger-core/wiki or
http://swagger.wordnik.com


Why do I want it?
-----------------

* You want your API to be easy to read.
* You want other people to be able to use your API easily.
* You'd like to build a really cool API explorer.
* It's Friday night and your friend just ditched on milkshakes.


How do I get it?
----------------

Currently, you clone this Github repository and drop the
flask_sillywalk.py file into your Python path, but this is not the
long-term answer. I'm looking to make this a proper Flask extension.

How do I use it?
----------------

I'm glad you asked. In order to use this code, you need to first
instantiate a SwaggerApiRegistry, which will keep track of all your API
endpoints and documentation.

  from flask import Flaskfrom flask_sillywalk import SwaggerApiRegistry,
    ApiParameter, ApiErrorResponse

  app = Flask("my_api")
  registry = SwaggerApiRegistry(
    app,
    baseurl="http://my-api-site.com/api/v1")
  register = registry.register
  registerModel = registry.registerModel
