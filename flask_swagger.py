from collections import defaultdict
import json
import lxml

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


__APIVERSION__ = "1.0"
__SWAGGERVERSION__ = "1.0"
SUPPORTED_FORMATS = ["xml", "json"]


class SwaggerApiRegistry(object):
    def __init__(self, app=None, basepath="/"):
        self.basepath = basepath
        self.r = defaultdict(set)
        if app is not None:
            self.app = app
            self.init_app(self.app)

    def init_app(self, app):
        for fmt in SUPPORTED_FORMATS:
            app.add_url_rule(
                    "{0}/resources.{1}".format(
                        self.basepath.rstrip("/"),
                        fmt),
                    "resources",
                    self.jsonify(self.resources))

    def jsonify(self, f):
        def inner_func():
            return json.dumps(f())
        return inner_func

    def resources(self):
        resources = {
                "apiVersion": __APIVERSION__,
                "swaggerVersion": __SWAGGERVERSION__,
                "basePath": self.basepath,
                "apis": list()}
        for resource in self.r.keys():
            resources["apis"].append({
                    "path": resource + ".{format}",
                    "description": "" })
        return resources


    def register(self, path, methods=["GET"], properties={}, parameters=[]):
        def inner_func(f):
            if self.app is None:
                logger.error("You need to initialize {0} with a Flask app".format(
                    self.__class__.__name__))
                return f

            ## how to do .json and .xml
            self.app.add_url_rule(
                path,
                f.__name__,
                f,
                methods=methods)

            api_method = ApiEndpoint(
                method=f,
                path=path.replace(self.basepath, "/"),
                httpmethod=methods,
                properties=properties,
                parameters=parameters)

            self.r[api_method.resource].add(api_method)

        return inner_func


class ApiEndpoint(object):

    def __init__(self, method, path, httpmethod, properties={}, parameters=[]):

        self.method = method
        self.httpmethod = httpmethod
        self.path = path
        self.properties = properties
        self.parameters = parameters
        self.description = self.method.__doc__
        self.resource = self.path.lstrip("/").split("/")[0]

    # See https://github.com/wordnik/swagger-core/wiki/API-Declaration
    def document(self):
        return {
            "path": self.path,
            "description": self.description,
            "parameters": self.parameters,
            "properties": self.properties,
            "httpmethod": self.httpmethod
        }

    def __hash__(self):
        return hash("{0} {1}".format(self.method, self.path))

