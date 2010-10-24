import re
from StringIO import StringIO
from shopipy.data.fields import Field
from shopipy.util import SortedDict, etree

def get_declared_fields(bases, attrs, with_base_fields=True):
    """
    Create a list of form field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases').

    If 'with_base_fields' is True, all fields from the bases are used.
    Otherwise, only fields in the 'declared_fields' attribute on the bases are
    used. The distinction is useful in subclassing.
    Also integrates any additional media definitions
    """
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, '_fields'):
                fields = base._fields.items() + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, '_fields_declared'):
                fields = base.declared_fields.items() + fields

    return SortedDict(fields)

class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    '_fields', taking into account parent class '_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs['_fields'] = get_declared_fields(bases, attrs)
        new_class = super(DeclarativeFieldsMetaclass,
                     cls).__new__(cls, name, bases, attrs)
        return new_class

class BaseShopifyElement(object):
    __camel_case__ = re.compile(r'[A-Z][a-z]+')
    
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_meta'):
            # Build up a list of attributes that the Meta object will have.
            attrs = {}
            
            # If parent form class already has an inner Meta, the Meta we're
            # creating needs to inherit from the parent's inner meta.
            parent = (object,)
            if hasattr(cls, 'Meta'):
                parent = (cls.Meta, object)
            cls._meta = type('%sMeta' % cls.__name__, parent, attrs)()
        
        return object.__new__(cls, *args, **kwargs)
    
    def __init__(self, **kwargs):
        # Allow initialization of field values
        for key, value in kwargs.items():
            if key not in self._fields:
                raise TypeError("TypeError: %s got an unexpected keyword argument '%s'" % 
                                ("__init__", key))
            else:
                setattr(self, key, value)
    
    def __setattr__(self, name, value):
        if name in self._fields:
            field = self._fields[name]
            value = field.to_python(value)
            field.validate(value)
        object.__setattr__(self, name, value)
    
    @classmethod
    def parse_xml(cls, node):
        if isinstance(node, str):
            node = etree.parse(StringIO(node)).getroot()
        
        element = cls()
        xml_map = {}
        for field_name, field in element._fields.items():
            tag = field.xml_name or field_name
            xml_map[tag] = field_name, field
        
        for child in node:
            if child.tag not in xml_map:
                continue
            field_name, field = xml_map[child.tag]
            field_value = field.to_python(child)
            setattr(element, field_name, field_value)
        
        return element
    
    def to_xml(self, tag):
        # TODO: Not Use Tag?
        node = etree.Element(tag, getattr(self._meta, 'xml_attributes', {}))
        for name, field in self._fields.items():
            try:
                value = getattr(self, name)
            except AttributeError:
                continue
            else:
                child_node = field.to_xml(value, name)
                node.append(child_node)
        return node

class ShopifyElement(BaseShopifyElement):
    "A collection of Fields, plus their associated data."
    # This is a separate class from BaseShopifyElement in order to abstract 
    # the way self.fields is specified. This class (ShopifyElement) is the 
    # one that does the fancy metaclass stuff purely for the semantic sugar.
    # It allows one to define a form using declarative syntax.
    # BaseShopifyElement itself has no way of designating self.fields.
    __metaclass__ = DeclarativeFieldsMetaclass
    