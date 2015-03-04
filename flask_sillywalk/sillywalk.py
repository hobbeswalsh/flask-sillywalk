import inspect
import json

from collections import defaultdict
from flask.ext.sillywalk.compat import urlparse


__SWAGGERVERSION__ = "1.3"
SUPPORTED_FORMATS = ["json"]


class SwaggerRegistryError(Exception):
    """A Swagger registry error"""
    pass


class SwaggerApiRegistry(object):
    """
    If you're going to make your Python/Flask API swagger compliant, you'll need
    to initialize a SwaggerApiRegistry with a Flask app and a baseurl.

    >>> my_app = Flask(__name__)
    >>> registry = SwaggerApiRegistry(my_app, "http://my_url.com/api/v1")

    Then you can register URLs with this class' "register" method.
    """

    def __init__(self, app=None, baseurl="http://localhost/",
                 api_version="1.0", api_descriptions={}):
        self.baseurl = baseurl
        self.api_version = api_version
        self.api_descriptions = api_descriptions
        self.basepath = urlparse(self.baseurl).path
        self.r = defaultdict(dict)
        self.models = defaultdict(dict)
        self.registered_routes = []
        if app is not None:
            self.app = app
            self.init_app(self.app)

    def init_app(self, app):
        """
        Initialize the Flask app by adding the base "resources" URL. Currently only JSON
        is supported, so this will add the URL <baseurl>/resources.json to your app.
        """
        for fmt in SUPPORTED_FORMATS:
            app.add_url_rule(
                "{0}/resources.{1}".format(
                    self.basepath.rstrip("/"),
                    fmt),
                "resources",
                self.jsonify(self.resources))

    def jsonify(self, f):
        """
        In case we need to serialize different stuff in the future.
        """

        def inner_func():
            return json.dumps(f())

        return inner_func

    def resources(self):
        """
        Gets all currently known API resources and serialized them.
        """
        resources = {
            "apiVersion": self.api_version,
            "swaggerVersion": __SWAGGERVERSION__,
            "basePath": self.baseurl,
            "models": dict(),
            "apis": list()}
        for resource in self.r.keys():
            description = (self.api_descriptions[resource]
                           if resource in self.api_descriptions else "")
            resources["apis"].append({
                "path": "/" + resource + ".{format}",
                "description": description})
        for k, v in self.models.items():
            resources["models"][k] = v
        return resources

    def registerModel(self,
                      type_="object"):
        """
        Registers a Swagger Model (object).

        Usage:

        >>> @my_registry.registerModel(type="Animal")
        >>> class Dog(object):
        >>>     def __init__(self):
        >>>     pass
        """

        def inner_func(c, *args, **kwargs):
            if self.app is None:
                raise SwaggerRegistryError(
                    "You need to initialize {0} with a Flask app".format(
                        self.__class__.__name__))
            self.models[c.__name__] = {
                "id": c.__name__,
                "description": c.__doc__ if c.__doc__ is not None else "",
                "type": type_,
                "properties": dict()}
            argspec = inspect.getargspec(c.__init__)
            argspec.args.remove("self")
            defaults = {}
            if argspec.defaults:
                defaults = list(zip(argspec.args[-len(
                    argspec.defaults):], argspec.defaults))
            for arg in argspec.args[:-len(defaults)]:
                if self.models[c.__name__].get("required") is None:
                    self.models[c.__name__]["required"] = []
                self.models[c.__name__]["required"].append(arg)
                # self.models[c.__name__]["required"][arg] = {"required": True}
            for k, v in defaults:
                self.models[c.__name__]["properties"][k] = {"default": v}
            return c

        return inner_func

    def _register(self,
                  path,
                  f,
                  method,
                  content_type,
                  parameters,
                  responseMessages,
                  nickname,
                  notes,
                  bp):

        if self.app is None:
            raise SwaggerRegistryError(
                "You need to initialize {0} with a Flask app".format(
                    self.__class__.__name__))

        # use basepath if not set by user
        if self.basepath not in path:
            path = self.basepath + "/" + path
            path = path.replace("//", "/")

        # register views on blueprints
        app = self.app

        if bp:
            app = bp

        app.add_url_rule(
            path,
            f.__name__,
            f,
            methods=[method])

        api = Api(
            method=f,
            path=path.replace(self.basepath, ""),
            httpMethod=method,
            params=parameters,
            responseMessages=responseMessages,
            nickname=nickname,
            notes=notes)

        if api.resource not in self.app.view_functions:
            for fmt in SUPPORTED_FORMATS:
                route = "{0}/{1}.{2}".format(self.basepath.rstrip("/"),
                                             api.resource, fmt)
                if route not in self.registered_routes:
                    self.registered_routes.append(route)
                    self.app.add_url_rule(
                        route,
                        api.resource,
                        self.show_resource(api.resource))

        if self.r[api.resource].get(api.path) is None:
            self.r[api.resource][api.path] = list()
        self.r[api.resource][api.path].append(api)

    def add_register(self,
                     path,
                     f,
                     method="GET",
                     content_type="application/json",
                     parameters=[],
                     responseMessages=[],
                     nickname=None,
                     notes=None,
                     bp=None):
        """
        Registers an API endpoint.

        Usage:

        >>> def get_cheese(cheesename):
        >>>     # some function
        >>> my_registry.add_register(
        ...     "/api/v1/cheese/<cheeseName>",
        ...     get_cheese,
        ...     parameters=[ApiParameter(
        ...         name="cheeseName",
        ...         description="The name of the cheese to fetch",
        ...         required=True,
        ...         dataType="str",
        ...         paramType="path",
        ...         allowMultiple=False)],
        ...     notes='For getting cheese, you know...',
        ...     responseMessages=[
        ...         ApiErrorResponse(400, "Sorry, we're fresh out of that cheese."),
        ...         ApiErrorResponse(418, "I'm actually a teapot")]))

        """
        self._register(path, f, method, content_type, parameters,
                       responseMessages, nickname, notes, bp)

    def register(self,
                 path,
                 method="GET",
                 content_type="application/json",
                 parameters=[],
                 responseMessages=[],
                 nickname=None,
                 notes=None,
                 bp=None):
        """
        Registers an API endpoint.

        Usage:

        >>> @my_registry.register(
        ...     "/api/v1/cheese/<cheeseName>",
        ...     parameters=[ApiParameter(
        ...         name="cheeseName",
        ...         description="The name of the cheese to fetch",
        ...         required=True,
        ...         dataType="str",
        ...         paramType="path",
        ...         allowMultiple=False)],
        ...     notes='For getting cheese, you know...',
        ...     responseMessages=[
        ...         ApiErrorResponse(400, "Sorry, we're fresh out of that cheese."),
        ...         ApiErrorResponse(418, "I'm actually a teapot")]))
        >>> def get_cheese(cheesename):
        >>>     # some function

        """
        def inner_func(f):
            self._register(path, f, method, content_type, parameters,
                           responseMessages, nickname, notes, bp)
        return inner_func

    def show_resource(self, resource):
        """
        Serialize a single resource.
        """

        def inner_func():
            return_value = {
                "resourcePath": resource.rstrip("/"),
                "apiVersion": self.api_version,
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
    """
    A documentable swagger object, e.g. an API endpoint, an API parameter, an API error response...
    """

    def document(self):
        return self.__dict__


class Api(SwaggerDocumentable):
    """
    A single API endpoint.
    """

    def __init__(
            self,
            method,
            path,
            httpMethod,
            params=None,
            responseMessages=None,
            nickname=None,
            notes=None):
        self.httpMethod = httpMethod
        self.summary = method.__doc__ if method.__doc__ is not None else ""
        self.resource = path.lstrip("/").split("/")[0]
        self.path = path.replace("<", "{").replace(">", "}")
        self.parameters = [] if params is None else params
        self.responseMessages = [] if responseMessages is None else responseMessages
        self.nickname = "" if nickname is None else nickname
        self.notes = notes

    # See https://github.com/wordnik/swagger-core/wiki/API-Declaration
    def document(self):
        ret = self.__dict__.copy()
        # need to serialize these guys
        ret["parameters"] = [p.document() for p in self.parameters]
        ret["responseMessages"] = [e.document() for e in self.responseMessages]
        return ret

    def __hash__(self):
        return hash(self.path)


class ApiParameter(SwaggerDocumentable):
    """
    A single API parameter
    """

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
    """
    Not sure what I was thinking here... --hobbeswalsh
    """

    def __init__(self, *args, **kwargs):
        if "default_value" not in kwargs:
            raise TypeError(
                "You need to provide an implicit param with a default value.")
        super(ImplicitApiParameter, self).__init__(*args, **kwargs)
        self.defaultValue = kwargs.get("default_value")


class ApiErrorResponse(SwaggerDocumentable):
    """
    An API error response.
    """

    def __init__(self, code, message):
        self.message = message
        self.code = code
