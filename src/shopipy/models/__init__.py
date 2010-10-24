# 
# I "statically type" the ShopifyElements to allow variable coercion
# when serializing from a new element to XML. It is a bit more rigid than
# dynamically typing everything, but hopefully the pillaged field system
# eases maintenance overhead.
# -Erik Karulf
# 10/6/2010
# 

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

