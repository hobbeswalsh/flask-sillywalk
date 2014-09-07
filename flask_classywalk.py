from flask_classy import FlaskView
from flask_classy import get_interesting_members

from flask_sillywalk import SUPPORTED_FORMATS, SwaggerApiRegistry, Api


def api_docs(parameters, response_messages):
    """A decorator that is used to define parameters, response_messages
    """

    def decorator(f):
        f._api_docs = {'parameters': parameters,
                       'error_response': response_messages}
        return f

    return decorator


class SwaggerClassyApiRegistry(SwaggerApiRegistry):

    def register_classy(self, klass):
        """
        Registers flask-classy endpoints.
        """

        if self.app is None:
            raise SwaggerRegistryError(
                "You need to initialize {0} with a Flask app".format(
                    self.__class__.__name__))

        for http_method, method in get_interesting_members(FlaskView, klass):
            paths = [(klass.route_base, [http_method])]
            try:
                method_routes = method._rule_cache[method.__func__.__name__]
            except AttributeError, KeyError:
                pass
            else:
                paths = [(klass.route_base.rstrip("/") +  _path,
                          _methods['methods']) for _path, _methods in method_routes]

            for route_path, route_methods in paths:
                for _method in route_methods:
                    api_docs = getattr(method, '_api_docs', {'parameters': [],
                                                             'error_response': []})
                    api = Api(
                        method=method,
                        path=route_path,
                        httpMethod=_method,
                        params=api_docs['parameters'],
                        responseMessages=api_docs['error_response'])

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
