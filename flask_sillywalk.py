import inspect
import json
from collections import defaultdict
from urlparse import urlparse

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


__APIVERSION__ = "1.0"
__SWAGGERVERSION__ = "1.0"
SUPPORTED_FORMATS = ["json"]


class SwaggerRegistryError(Exception):
    pass


class SwaggerApiRegistry(object):

    def __init__(self, app=None, baseurl="http://localhost/"):
        self.baseurl = baseurl
        self.basepath = urlparse(self.baseurl).path
        self.r = defaultdict(dict)
        self.models = defaultdict(dict)
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
            "basePath": self.baseurl,
            "models": dict(),
            "apis": list()}
        for resource in self.r.keys():
            resources["apis"].append({
                "path": "/" + resource + ".{format}",
                "description": ""})
        for k, v in self.models.items():
            resources["models"][k] = v
        return resources

    def registerModel(self,
                      c,
                      type_="object"):
        def inner_func(*args, **kwargs):
            if self.app is None:
                raise SwaggerRegistryError(
                    "You need to initialize {0} with a Flask app".format(
                        self.__class__.__name__))
            return c(*args, **kwargs)
        self.models[c.__name__] = {
            "id": c.__name__,
            "type": type_,
            "properties": dict()}
        argspec = inspect.getargspec(c.__init__)
        argspec.args.remove("self")
        defaults = {}
        if argspec.defaults:
            defaults = zip(argspec.args[-len(
                argspec.defaults):], argspec.defaults)
        for arg in argspec.args[:-len(defaults)]:
            self.models[c.__name__]["properties"][arg] = {"required": True}
        for k, v in defaults:
            self.models[c.__name__]["properties"][k] = {
                "required": False,
                "default": v}
        return inner_func

    def register(
            self,
            path,
            method="GET",
            content_type="application/json",
            parameters=[],
            errorResponses=[],
            notes=None):
        def inner_func(f):
            if self.app is None:
                raise SwaggerRegistryError(
                    "You need to initialize {0} with a Flask app".format(
                        self.__class__.__name__))

            self.app.add_url_rule(
                path,
                f.__name__,
                f,
                methods=[method])

            api = Api(
                method=f,
                path=path.replace(self.basepath, ""),
                httpMethod=method,
                params=parameters,
                errorResponses=errorResponses,
                notes=notes)

            if api.resource not in self.app.view_functions:
                for fmt in SUPPORTED_FORMATS:
                    self.app.add_url_rule(
                        "{0}/{1}.{2}".format(
                        self.basepath.rstrip("/"),
                        api.resource,
                        fmt),
                        api.resource,
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


class SwaggerDocumentable(object):

    def document(self):
        return self.__dict__


class Api(SwaggerDocumentable):

    def __init__(
            self,
            method,
            path,
            httpMethod,
            params=None,
            errorResponses=None,
            nickname=None,
            notes=None):

        self.httpMethod = httpMethod
        self.summary = method.__doc__ if method.__doc__ is not None else ""
        self.resource = path.lstrip("/").split("/")[0]
        self.path = path.replace("<", "{").replace(">", "}")
        self.parameters = [] if params is None else params
        self.errorResponses = [] if errorResponses is None else errorResponses
        self.nickname = "" if nickname is None else nickname
        self.notes = notes

    # See https://github.com/wordnik/swagger-core/wiki/API-Declaration
    def document(self):
        ret = self.__dict__.copy()
        # need to serialize these guys
        ret["parameters"] = [p.document() for p in self.parameters]
        ret["errorResponses"] = [e.document() for e in self.errorResponses]
        return ret

    def __hash__(self):
        return hash(self.path)


class ApiParameter(SwaggerDocumentable):

    def __init__(
            self,
            name,
            description,
            required,
            dataType,
            paramType,
            allowMultiple=False):
        self.name = name
        self.description = description
        self.required = required
        self.dataType = dataType
        self.paramType = paramType
        self.allowMultiple = allowMultiple

    def document(self):
        return self.__dict__


class ImplicitApiParameter(ApiParameter):

    def __init__(self, *args, **kwargs):
        if "default_value" not in kwargs:
            raise TypeError(
                "You need to provide an implicit parameter with a default value.")
        super(ImplicitApiParameter, self).__init__(*args, **kwargs)
        self.defaultValue = kwargs.get("default_value")


class ApiErrorResponse(SwaggerDocumentable):

    def __init__(self, code, message):
        self.message = message
        self.code = code
