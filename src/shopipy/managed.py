import urllib
import urllib2
import re

from decimal import Decimal
from datetime import datetime
from shopipy.util import generate_url, parse_xml, etree
from shopipy.data.models import ShopifyElement
from shopipy.data.fields import *

class ShopifyAPI(object):
    CLASSES = ['ApplicationCharge', 'RecurringApplicationCharge', 'Article',
               'Asset', 'Blog', 'Collect', 'Comment', 'Country',
               'CustomCollection', 'Fulfillment', 'Metafield', 'Order', 'Page',
               'Product', 'ProductImage', 'ProductVariant', 'Province',
               'Redirect', 'Shop', 'SmartCollection', 'Transactions', 'Webhook']
    @staticmethod
    def format_datetime(dt):
        s = dt.strftime("%Y-%m-%dT%H:%M")
        tz = dt.utcoffset()
        return "{0:%Y-%m-%dT%H:%M}{1:0=+3}:{2:0=2}".format(dt, tz.hour, tz.minute)

# 
# I "statically type" the ShopifyElements to allow variable coercion
# when serializing from a new element to XML. It is a bit more rigid than
# dynamically typing everything, but hopefully the pillaged field system
# eases maintenance overhead.
# -Erik Karulf
# 10/6/2010
# 

class Address(ShopifyElement):
    first_name      = StringField(xml_name="first-name")
    last_name       = StringField(xml_name="last-name")
    name            = StringField()
    company         = StringField()
    address1        = StringField()
    address2        = StringField()
    city            = StringField()
    country         = StringField()
    phone           = StringField()
    province        = StringField()
    postal_code     = StringField(xml_name="zip")
    country_code    = StringField(xml_name="country-code")
    province_code   = StringField(xml_name="province-code")

class LineItem(ShopifyElement):
    shopify_id      = IntegerField(xml_name="id")
    price           = DecimalField()
    product_id      = IntegerField(xml_name="product-id")
    quantity        = IntegerField()
    requires_shipping = BooleanField()
    sku             = StringField()
    title           = StringField()
    variant_id      = IntegerField(xml_name="variant-id")
    variant_title   = StringField(xml_name="variant-title")
    vendor          = StringField()
    name            = StringField()

class ShippingLine(ShopifyElement):
    code            = StringField()
    price           = DecimalField()
    title           = StringField()

class TaxLine(ShopifyElement):
    price           = DecimalField()
    rate            = FloatField()
    title           = StringField()

class NoteAttribute(ShopifyElement):
    name            = StringField()
    value           = StringField()

class Order(ShopifyElement):
    shopify_id              = IntegerField(xml_name="id")
    buyer_accepts_marketing = BooleanField(xml_name="buyer-accepts-marketing")
    closed_at               = DateTimeField(xml_name="closed-at")
    created_at              = DateTimeField(xml_name="created-at")
    currency                = StringField()
    email                   = StringField()
    financial_status        = StringField(xml_name="financial-status")
    fulfillment_status      = StringField(xml_name="fulfillment-status")
    gateway                 = StringField()
    landing_site            = StringField(xml_name="landing-site")
    name                    = StringField()
    note                    = StringField()
    number                  = IntegerField()
    referring_site          = StringField(xml_name="referring-site")
    subtotal_price          = DecimalField(xml_name="subtotal-price")
    taxes_included          = BooleanField(xml_name="taxes-included")
    token                   = StringField()
    total_discounts         = DecimalField(xml_name="total-discounts")
    total_line_items_price  = DecimalField(xml_name="total-line-items-price")
    total_price             = DecimalField(xml_name="total-price")
    total_tax               = DecimalField(xml_name="total-tax")
    total_weight            = IntegerField(xml_name="total-weight")
    updated_at              = DateTimeField(xml_name="updated-at")
    browser_ip              = StringField(xml_name="browser-ip")
    landing_site_ref        = StringField(xml_name="landing-site-ref")
    order_number            = IntegerField(xml_name="order-name")
    billing_address         = ElementField(Address, xml_name="billing-address")
    shipping_address        = ElementField(Address, xml_name="shipping-address")
    line_items              = ArrayField(LineItem, xml_name="line-items", child_xml_name="line-item")
    shipping_lines          = ArrayField(ShippingLine, xml_name="shipping-lines", child_xml_name="shipping-line")
    tax_lines               = ArrayField(TaxLine, xml_name="tax-lines", child_xml_name="tax-line")
    note_attributes         = ArrayField(NoteAttribute, xml_name="note-attributes", child_xml_name="note-attribute")
