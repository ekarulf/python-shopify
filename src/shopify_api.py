#!/usr/bin/env python
# Copyright 2011 Erik Karulf. All Rights Reserved.

import inspect
import new

from pyactiveresource.activeresource import ActiveResource
from pyactiveresource.connection import Connection
from shopify import util

def _remote_resources():
    remote = []
    resources = __import__('shopify.resources', fromlist=['__all__'])
    for name in dir(resources):
        resource = getattr(resources, name)
        if inspect.isclass(resource) and issubclass(resource, ShopifyResource):
            remote.append(resource)
    return remote


class Countable(object):
    def count(self, **options):
        return self.get('count', **options).get('count')


class ShopifyResource(ActiveResource, Countable):
    pass


class MetafieldResource(object):
    def metafields(self):
        return self.session.Metafield.find(resource=self.plural,
                                           resource_id=self.id)

    def add_metafield(self, metafield):
        if not hasattr(self.id):
            raise (ArgumentError, "You can only add metafields to resource"
                                  " that has been saved")

        metafield.prefix_options = {
            'resource': self.plural,
            'resource_id': self.id,
        }

        metafield.save()
        return metafield


class EventResource(object):
    def events(self):
        return self.session.Events.find(resource=self.plural,
                                        resource_id=self.id)


# Session must remain at the bottom of the file to ease circular imports
class Session(Connection):
    def __init__(self, domain, api_key, secret, token=None, protocol='https'):
        user = api_key
        if token:
            password = util.md5(secret + token).hexdigest()
        else:
            password = secret
        site = "%s://%s/" % (protocol, domain)

        super(Session, self).__init__(site, user, password)

        for resource in _remote_resources():
            name = resource.__name__
            resource_class = new.classobj(name, (resource,), {})
            resource_class._connection = resource_class.session = self
            setattr(self, name, resource_class)


