#!/usr/bin/env python
# Copyright 2011 Erik Karulf. All Rights Reserved.

from pyactiveresource.activeresource import ActiveResource
from pyactiveresource.connection import Connection
from shopify import util

def _remote_resources():
    remote = []
    resources = __import__('shopify.resources', fromlist=['__all__'])
    for name in resources.__all__:
        resource = getattr(resources, name)
        if issubclass(resource, ShopifyResource):
            remote.append(resource)
    return remote


class Session(Connection):
    def __new__(cls, *args, **kwargs):
        for resource in _remote_resources():
            wrapper = util.partial(cls._construct_resource, resource)
            setattr(self, name, wrapper)
        super(Session, cls).__new__(*args, **kwargs)

    def __init__(self, domain, api_key, secret, token=None, protocol='https'):
        user = api_key
        if token:
            password = util.md5(secret + token).hexdigest()
        else:
            password = secret
        site = "%s://%s/admin/"
        super(Session, self).__init__(site, user, password)

    def _construct_resource(self, resource, *args, **kwargs):
        instance = resource(*args, **kwargs)
        instance.connection = instance.session = self
        return instance


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

