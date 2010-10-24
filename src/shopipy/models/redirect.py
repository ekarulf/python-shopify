from shopipy.data.fields import *
from shopipy.data.models import ShopifyElement

class Redirect(ShopifyElement):
    shopify_id      = IntegerField(xml_name="id")
    path            = StringField()
    target          = StringField()

