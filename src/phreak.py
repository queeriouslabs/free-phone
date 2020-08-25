class OverlappingRoute(Exception):
    def __init__(self, number):
        self.number = number


def prefix(a, b):
    return a[:len(b)] == b or b[:len(a)] == a


class Phlask(object):

    def __init__(self, name):
        self.name = name
        self.routes = {
            'parts': {}
        }

    def route(self, number):
        def decorator(handler):
            self.add_route(number, handler)

        return decorator

    def add_route(self, number, handler):
        parts = number.split('/')
        if not self.safe_route(parts):
            raise OverlappingRoute(number)

        self.insert_route(parts, handler)

    def insert_route(self, parts, handler):
        if len(parts) < 1:
            raise

        node = self.routes
        for part in parts:
            if part not in node['parts']:
                node['parts'][part] = {'parts': {}}
            node = node['parts'][part]

        node['handler'] = handler

    def safe_route(self, parts):
        node = self.routes
        for part in parts:
            if node in parts:
                node = node['parts']
            else:
                for other in node['parts']:
                    if prefix(part, other):
                        return False
        return True

    def dispatch(self, parts):
        node = self.routes
        for part in parts:
            if part not in node['parts']:
                self.route_missing(parts)
                return

        if 'callback' not in node:
            self.route_missing(parts)
        else:
            return node['callback']()

    def route_missing(self, parts):
        pass
