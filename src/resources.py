#!/usr/bin/env python
# Copyright 2011 Erik Karulf. All Rights Reserved.

import base64
from shopify.shopify_api import ShopifyResource, MetafieldResource, EventResource
from shopify import util


class Shop(ShopifyResource):
    def current(self):
        return self.find_one(from_=self.prefix)

    def shop(self):
        return self.current()

    def events(self):
        return self.session.Event.find()


class Event(ShopifyResource):
    pass


class CustomCollection(ShopifyResource, MetafieldResource, EventResource):
    def products(self):
        return Product.find(collection_id=self.id)

    def add_product(self, product):
        return Collect.create({
            collection_id: self.id,
            product_id: product.id,
        })

    def remove_product(self, product):
        collect = self.session.Collect.find_first(collection_id=self.id,
                                                  product_id=product.id)
        if collect:
            collect.destroy()


class SmartCollection(ShopifyResource, MetafieldResource, EventResource):
    def products(self):
        return self.session.Product.find(collection_id=self.id)


# For adding/removing products from custom collections
class Collect(ShopifyResource):
    pass


class ShippingAddress(ShopifyResource):
    pass


class BillingAddress(ShopifyResource):
    pass


class LineItem(ShopifyResource):
    pass


class ShippingLine(ShopifyResource):
    pass


class NoteAttribute(ShopifyResource):
    pass


class Order(ShopifyResource, MetafieldResource, EventResource):
    def close(self):
        return self.post('close')

    def open(self):
        return self.post('open')

    def transactions(self):
        return self.session.Transaction.find(order_id=self.id)

    def capture(amount=""):
        return self.session.Transaction.create(amount=amount,
                                               kind="capture",
                                               order_id=self.id)


class Product(ShopifyResource, MetafieldResource, EventResource):
    # Share all items of this store with the
    # shopify marketplace
    # TODO: Undocumented methods
    def share(self):
        return self.post('share')

    def unshare(self):
        return self.delete('share')

    # compute the price range
    def price_range(self):
        prices = [price for variant in self.variants]
        prices.sort()
        if prices.min != prices.max:
            return "%0.2f - %0.2f" % (prices[0], prices[-1])
        else:
            return "%0.2f" % prices.min

    def collections(self):
        return self.session.CustomCollection.find(product_id=self.id)

    def smart_collections(self):
        return self.session.SmartCollection.find(product_id=self.id)

    def add_to_collection(collection):
        return collection.add_product(self)

    def remove_from_collection(collection):
        return collection.remove_product(self)


class Variant(ShopifyResource, MetafieldResource):
    product_prefix_source = "/products/${product_id}/"

    def prefix(self, options=None):
        if options is not None and 'product_id' in options:
            self.prefix_source = self.product_prefix_source
        return super(Variant, self).prefix(options)


class Image(ShopifyResource):
    prefix_source = "products/${product_id}/"
    sizes = ("pico", "icon", "thumb", "small", "compact", "medium", "large",
             "grande", "original")

    def _image_src(self, repl=""):
        re.sub(r"/\/(.*)\.(\w{2,4})/", repl, self.src)

    def __new__(cls, *args, **kwargs):
        for size in cls.sizes:
            # generate a method for each possible image variant
            repl = r"/\1_%s.\2" % size
            method = util.partial(cls._image_src, repl=repl)
            setattr(cls, method)

    def attach_image(self, data, filename=None):
        self.attachment = base64.b64encode(data)
        if filename:
            self.filename = filename
        self.save()


class Transaction(ShopifyResource):
    prefix_source = "orders/${order_id}/"


class Fulfillment(ShopifyResource):
    prefix_source = "orders/${order_id}/"


class Country(ShopifyResource):
    pass


class Page(ShopifyResource, MetafieldResource, EventResource):
    pass


class Blog(ShopifyResource, MetafieldResource, EventResource):
    def articles(self):
        return Article.find(blog_id=id)


class Article(ShopifyResource, MetafieldResource, EventResource):
    prefix_source = "blogs/${blog_id}/"


class Metafield(ShopifyResource):
    resource_prefix_source = "${resource}/${resource_id}/"

    def prefix(self, options=None):
        if options is not None and 'resource' in options:
            self.prefix_source = self.resource_prefix_source
        return super(Metafield, self).prefix(options)

    def value(self):
        value = attributes.get("value", None)
        value_type = attributes.get("value_type", None)
        if value_type == "integer":
            return int(value)
        else:
            return value


class Comment(ShopifyResource):
    def remove(self):
        return self.post('remove')

    def ham(self):
        return self.post('ham')

    def spam(self):
        return self.post('spam')

    def approve(self):
        return self.post('approve')


class Province(ShopifyResource):
    prefix_source = "countries/:country_id/"


class Redirect(ShopifyResource):
    pass


class Webhook(ShopifyResource):
    pass


class Event(ShopifyResource):
    resource_prefix_source = "${resource}/${resource_id}/"
    
    def prefix(self, options=None):
        if options is not None and 'resource' in options:
            self.prefix_source = self.resource_prefix_source
        return super(Event, self).prefix(options)


class Customer(ShopifyResource):
    pass


class CustomerGroup(ShopifyResource):
    pass


# Assets represent the files that comprise your theme.
# There are different buckets which hold different kinds
# of assets, each corresponding to one of the folders
# within a theme's zip file: layout, templates, and
# assets. The full key of an asset always starts with the
# bucket name, and the path separator is a forward slash,
# like layout/theme.liquid or assets/bg-body.gif.
#
# Initialize with a key:
#   asset = ShopifyAPI::Asset.new(:key => 'assets/special.css')
# 
# Find by key:
#   asset = ShopifyAPI::Asset.find('assets/image.png')
# 
# Get the text or binary value:
#   asset.value # decodes from attachment attribute if necessary
# 
# You can provide new data for assets in a few different ways:
# 
#   * assign text data for the value directly:
#       asset.value = "div.special {color:red;}"
#     
#   * provide binary data for the value:
#       asset.attach(File.read('image.png'))
#     
#   * set a URL from which Shopify will fetch the value:
#       asset.src = "http://mysite.com/image.png"
#     
#   * set a source key of another of your assets from which
#     the value will be copied:
#       asset.source_key = "assets/another_image.png"


class Asset(ShopifyResource):
    # find an asset by key:
    #   Asset.find('layout/theme.liquid')
    def find(path, **options):
        params = dict({'asset': {'key': path}}, **options)
        return self.find_one("assets.xml", **params)

    # For text assets, Shopify returns the data in the 'value' attribute.
    # For binary assets, the data is base-64-encoded and returned in the
    # 'attachment' attribute. This accessor returns the data in both cases.
    def value(self):
        if "value" in self.attributes:
            return self.value
        elif "attachment" in self.attributes:
            return bas64.b64decode(self.attachment)
        else:
            return None

    @property
    def attach(self, data):
        self.attachment = base64.b64encode(data)

class RecurringApplicationCharge(ShopifyResource):
    # TODO: undef_method :test ?

    def current(self):
        # TODO: Shopify should be filtering for us
        return filter(lambda charge: charge.status == 'active', self.find())

    def cancel(self):
        return self.post('destroy')

    def activate(self):
        return self.post('activate')


class ApplicationCharge(ShopifyResource):
    # TODO: undef_method :test ?
    def activate(self):
        return self.post('activate')


class ProductSearchEngine(ShopifyResource):
    pass


class ScriptTag(ShopifyResource):
    pass

