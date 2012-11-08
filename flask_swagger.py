from collections import defaultdict
import json
import lxml
from urlparse import urlparse

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


__APIVERSION__ = "1.0"
__SWAGGERVERSION__ = "1.0"
SUPPORTED_FORMATS = ["xml", "json"]


class SwaggerApiRegistry(object):
    def __init__(self, app=None, baseurl="http://localhost/"):
        self.baseurl = baseurl
        self.basepath = urlparse(self.baseurl).path
        self.r = defaultdict(dict)
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
                    ## XXX json / xml
                    self.jsonify(self.resources))

    def jsonify(self, f):
        def inner_func():
            return json.dumps(f())
        return inner_func

    def resources(self):
        resources = {
                "apiVersion": __APIVERSION__,
                "swaggerVersion": __SWAGGERVERSION__,
                "basePath": self.baseurl,
                "apis": list()}
        for resource in self.r.keys().keys():
            resources["apis"].append({
                    "path": resource + ".{format}",
                    "description": "" })
        return resources


    def register(self, path, method="GET", properties={}, parameters=[]):
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
                methods=[method])

            api = Api(
                method=f,
                path=path.replace(self.basepath, ""),
                httpmethod=method,
                properties=properties,
                parameters=parameters)

            if api.resource not in self.app.view_functions:
                for fmt in SUPPORTED_FORMATS:
                    self.app.add_url_rule(
                            "{0}/{1}.{2}".format(
                                self.basepath.rstrip("/"),
                                api.resource,
                                fmt),
                            api.resource,
                            ## XXX json / xml
                            self.show_resource(api.resource))

            if self.r[api.resource].get(api.path) is None:
                self.r[api.resource][api.path] = list()
            self.r[api.resource][api.path].append(api)

        return inner_func


    def show_resource(self, resource):
        def inner_func():
            return_value = {
                    "resourcePath": resource.rstrip("/"),
                    "apiVersion": __APIVERSION__,
                    "swaggerVersion": __SWAGGERVERSION__,
                    "basePath": self.baseurl,
                    "apis": list(),
                    "models": list()
            }
            resource_map = self.r.get(resource)
            for path, apis in resource_map.items():
                api_object = {
                        "path": path,
                        "description": "",
                        "operations": list()}
                for api in apis:
                    api_object["operations"].append(api.document())
                return_value["apis"].append(api_object)
            return json.dumps(return_value)
        return inner_func


class Api(object):

    def __init__(self, method, path, httpmethod, properties={}, parameters=[]):

        self.method = method
        self.httpmethod = httpmethod
        self.path = path.replace("<", "{").replace(">", "}")
        self.properties = properties
        self.parameters = parameters
        self.summary = self.method.__doc__ if self.method.__doc__ is not None else ""
        self.resource = self.path.lstrip("/").split("/")[0]

    # See https://github.com/wordnik/swagger-core/wiki/API-Declaration
    def document(self):
        return {
            "path": self.path,
            "summary": self.summary,
            "parameters": self.parameters,
            "properties": self.properties,
            "httpMethod": self.httpmethod
        }

    def __hash__(self):
        return hash(self.path)

