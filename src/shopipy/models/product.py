from shopipy.data.fields import *
from shopipy.data.models import ShopifyElement

class ProductVariant(ShopifyElement):
    shopify_id              = IntegerField(xml_name="id")
    product_id              = IntegerField(xml_name="product-id")
    created_at              = DateTimeField(xml_name="created-at")
    updated_at              = DateTimeField(xml_name="updated-at")
    sku                     = StringField()
    title                   = StringField()
    position                = IntegerField()
    option1                 = StringField()
    option2                 = StringField()
    option3                 = StringField()
    grams                   = IntegerField()
    requires_shipping       = BooleanField(xml_name="requires-shipping")
    fulfillment_service     = StringField(xml_name="fulfillment-service")
    inventory_management    = StringField(xml_name="inventory-management")
    inventory_policy        = StringField(xml_name="inventory-policy")
    inventory_quantity      = IntegerField(xml_name="inventory-quantity")
    price                   = DecimalField()
    compare_at_price        = DecimalField(xml_name="compare-at-price")
    taxable                 = BooleanField()

class ProductImage(ShopifyElement):
    shopify_id              = IntegerField(xml_name="id")
    product_id              = IntegerField(xml_name="product-id")
    created_at              = DateTimeField(xml_name="created-at")
    updated_at              = DateTimeField(xml_name="updated-at")
    position                = IntegerField()
    src                     = StringField()

class ProductOption(ShopifyElement):
    name                    = StringField()

class Product(ShopifyElement):
    shopify_id              = IntegerField(xml_name="id")
    handle                  = StringField()
    title                   = StringField()
    body_html               = StringField(xml_name="body-html")
    created_at              = DateTimeField(xml_name="created-at")
    updated_at              = DateTimeField(xml_name="updated-at")
    published_at            = DateTimeField(xml_name="published-at")
    template_suffix         = StringField(xml_name="template-suffix")
    product_type            = StringField(xml_name="product-type")
    vendor                  = StringField()
    tags                    = StringField() # TODO: Create a CSVField or TagField
    options                 = ArrayField(ProductOption, child_xml_name="option")
    variants                = ArrayField(ProductVariant, child_xml_name="variant")
    images                  = ArrayField(ProductImage, child_xml_name="image")

    