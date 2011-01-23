#!/usr/bin/env python
# Copyright 2011 Erik Karulf. All Rights Reserved.

import base64
from pyactiveresource import ActiveResource
from shopify import util

# FIXME: Session + Authentication!
# FIXME: Decorators
# FIXME: Directory structure?


class Session(object):
    def __init__(self, api_key, secret, protocol='https'):
        self.api_key = api_key
        self.secret = secret
        self.protocol = protocol

    def initialize(self, url, token, params):
        pass


class Countable(object):
    def count(self, **options):
        return self.get('count', **options).get('count')


class Base(ActiveResource, Countable):
    pass


class Shop(Base):
    def current(self):
        return self.find_one(from=self.prefix)

    def shop(self):
        return self.current()

    def events(self):
        return Event.find()


class Event(Base):
    pass


@MetafieldResource
@EventResource
class CustomCollection(Base):
    def products(self):
        return Product.find(collection_id=self.id)

    def add_product(self, product):
        return Collect.create({
            collection_id: self.id,
            product_id: product.id,
        })

    def remove_product(self, product):
        collect = Collect.find_first(collection_id=self.id,
                                     product_id=product.id)
        if collect:
            collect.destroy()


@MetafieldResource
@EventResource
class SmartCollection(Base):
    def products(self):
        return Product.find(collection_id=self.id)


# For adding/removing products from custom collections
class Collect(Base):
    pass


class ShippingAddress(Base):
    pass


class BillingAddress(Base):
    pass


class LineItem(Base):
    pass


class ShippingLine(Base):
    pass


class NoteAttribute(Base):
    pass


@MetafieldResource
@EventResource
class Order(Base):
    def close(self):
        return self.post('close')

    def open(self):
        return self.post('open')

    def transactions(self):
        return Transaction.find(order_id=self.id)

    def capture(amount=""):
        return Transaction.create(amount=amount,
                                  kind="capture",
                                  order_id=self.id)


@MetafieldResource
@EventResource
class Product(Base):
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
        return CustomCollection.find(product_id=self.id)

    def smart_collections(self):
        SmartCollection.find(product_id=self.id)

    def add_to_collection(collection):
        return collection.add_product(self)

    def remove_from_collection(collection):
        return collection.remove_product(self)


@MetafieldResource
class Variant(Base):
    product_prefix_source = "/admin/products/${product_id}/"

    def prefix(self, options=None):
        """Return the prefix for Variant based on the presence of product_id

        Args:
            options: A dictionary containing additional prefixes to prepend.
        Returns:
            A string containing the path to this element.
        """
        if options is not None and 'product_id' in options:
            self.prefix_source = self.product_prefix_source
        return super(Variant, self).prefix(options)


class Image(Base):
    prefix_source = "/admin/products/${product_id}/"
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


class Transaction(Base):
    prefix_source = "/admin/orders/${order_id}/"


class Fulfillment(Base):
    prefix_source = "/admin/orders/${order_id}/"


class Country(Base):
    pass


@MetafieldResource
@EventResource
class Page(Base):
    pass


@MetafieldResource
@EventResource
class Blog(Base):
    def articles(self):
        return Article.find(blog_id=id)


@MetafieldResource
@EventResource
class Article(Base):
    prefix_source = "/admin/blogs/${blog_id}/"


class Metafield(Base):
    resource_prefix_source = "/admin/${resource}/${resource_id}/"
    shop_prefix_source = "/admin/"

    def prefix(self, options=None):
        """Return the prefix for Variant based on the presence of resource

        Args:
            options: A dictionary containing additional prefixes to prepend.
        Returns:
            A string containing the path to this element.
        """
        if options is not None and 'resource' in options:
            self.prefix_source = self.resource_prefix_source
        else:
            self.prefix_source = self.shop_prefix_source
        return super(Metafield, self).prefix(options)

    def value(self):
        value = attributes.get("value", None)
        value_type = attributes.get("value_type", None)
        if value_type == "integer":
            return int(value)
        else:
            return value


class Comment(Base):
    def remove(self):
        return self.post('remove')

    def ham(self):
        return self.post('ham')

    def spam(self):
        return self.post('spam')

    def approve(self):
        return self.post('approve')


class Province(Base):
    prefix_source = "/admin/countries/:country_id/"


class Redirect(Base):
    pass


class Webhook(Base):
    pass


class Event(Base):
    resource_prefix_source = "/admin/${resource}/${resource_id}/"
    shop_prefix_source = "/admin/"
    
    def prefix(self, options=None):
        """Return the prefix for Variant based on the presence of resource

        Args:
            options: A dictionary containing additional prefixes to prepend.
        Returns:
            A string containing the path to this element.
        """
        if options is not None and 'resource' in options:
            self.prefix_source = self.resource_prefix_source
        else:
            self.prefix_source = self.shop_prefix_source
        return super(Event, self).prefix(options)


class Customer(Base):
    pass


class CustomerGroup(Base):
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


class Asset(Base):
    # TODO: Asset is complex!
    """
    primary_key = 'key'
    # find an asset by key:
    #   ShopifyAPI::Asset.find('layout/theme.liquid')
    def self.find(*args)
      if args[0].is_a?(Symbol)
        super
      else
        params = {:asset => {:key => args[0]}}
        params = params.merge(args[1][:params]) if args[1] && args[1][:params]
        find(:one, :from => "/admin/assets.#{format.extension}", :params => params)
      end
    end

    # For text assets, Shopify returns the data in the 'value' attribute.
    # For binary assets, the data is base-64-encoded and returned in the
    # 'attachment' attribute. This accessor returns the data in both cases.
    def value
      attributes['value'] ||
      (attributes['attachment'] ? Base64.decode64(attributes['attachment']) : nil)
    end

    def attach(data)
      self.attachment = Base64.encode64(data)
    end

    def destroy #:nodoc:
      connection.delete(element_path(:asset => {:key => key}), self.class.headers)
    end

    def new? #:nodoc:
      false
    end

    def self.element_path(id, prefix_options = {}, query_options = nil) #:nodoc:
      prefix_options, query_options = split_options(prefix_options) if query_options.nil?
      "#{prefix(prefix_options)}#{collection_name}.#{format.extension}#{query_string(query_options)}"
    end

    def method_missing(method_symbol, *arguments) #:nodoc:
      if %w{value= attachment= src= source_key=}.include?(method_symbol)
        wipe_value_attributes
      end
      super
    end

    private

    def wipe_value_attributes
      %w{value attachment src source_key}.each do |attr|
        attributes.delete(attr)
      end
    end
    end
    """


class RecurringApplicationCharge(Base):
    # TODO: undef_method :test ?

    def current(self):
        # TODO: Shopify should be filtering for us
        return filter(lambda charge: charge.status == 'active', self.find())

    def cancel(self):
        return self.post('destroy')

    def activate(self):
        return self.post('activate')


class ApplicationCharge(Base):
    # TODO: undef_method :test ?
    def activate(self):
        return self.post('activate')


class ProductSearchEngine(Base):
    pass


class ScriptTag(Base):
    pass

