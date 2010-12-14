"""
This is losely based off of the Django field system
Fields are kept in a class dictionary and used to validate input
"""
import re
import dateutil.parser
from decimal import Decimal, DecimalException
from datetime import datetime, time, date
from shopipy.util import etree, etree_element, parse_xml
from shopipy.exceptions import ValidationError

EMPTY_VALUES = (None, '', [], (), {})

class FieldValue(object):
    __slots__ = ('value', 'field') 

    def __init__(self, field, value=None):
        self.field = field
        self.value = value

    def __repr__(self):
        return '%sValue(value=%s)' % (self.field.__name__, repr(self.value))

    def __get__(self, instance, owner):
        return self.value
    
    def __set__(self, instance, value):
        self.value = self.field.to_python(value)
    
    def __delete__(self, instance):
        if self.field._meta.required:
            raise AttributeError("Field is required")
        self.value = None

class Field(object):
    default_error_messages = {
        'required': 'This field is required.',
        'invalid':  'Enter a valid value.',
    }
    
    def __new__(cls, *args, **kwargs):
        messages = {}
        xml_attributes = {}
        for c in reversed(cls.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
            xml_attributes.update(getattr(c, 'default_xml_attributes', {}))
        cls.error_messages = messages
        cls.xml_attributes = xml_attributes
        return object.__new__(cls, *args, **kwargs)
    
    def __init__(self, required=False, xml_name=None):
        self.required = required
        self.xml_name = xml_name
        self.validators = []
    
    def set_value(self, value):
        value = self.to_python(value)
        self.validate(value)
        self._value = value
        return self._value
    
    def get_value(self):
        return self._value
    
    value = property(get_value, set_value)
    
    def validate(self, value):
        if value in EMPTY_VALUES and self.required:
            raise ValidationError(self.error_messages['required'])
        
        for validator in self.validators:
            if not validator(value):
                if hasattr(validator, 'description'):
                    raise ValidationError("ValidationError: %s" % validator.description)
                else:
                    raise ValidationError("ValidationError: Failed %s check" % validator.__name__)
    
    def to_python(self, value):
        if isinstance(value, etree_element):
            if 'nil' in value.attrib:
                return None
            return value.text
        raise ValueError("Expected ElementTree Element")
    
    def to_xml(self, value, tag):
        name = self.xml_name or tag
        node = etree.Element(name, attrib=self.xml_attributes)
        if value is None:
            node.attrib['nil'] = 'true'
            assert 'nil' not in self.xml_attributes
        return node

class StringField(Field):
    default_error_messages = {
        'invalid': 'Enter a non-zero length string.',
    }
    
    def to_python(self, value):
        "Returns a Unicode object."
        if isinstance(value, etree_element):
            value = value.text
        return value
    
    def to_xml(self, value, tag):
        node = super(StringField, self).to_xml(value, tag)
        if value:
            node.text = value
        return node


class BooleanField(Field):
    default_error_messages = {
        'invalid': 'Enter true or false.',
    }
    default_xml_attributes = {
        'type': 'boolean',
    }

    def to_python(self, value):
        """Returns a Python boolean object."""
        # Explicitly check for the string 'False', which is what a hidden field
        # will submit for False. Also check for '0'.
        # Because bool("True") == bool('1') == True, we don't need to handle
        # that explicitly.
        if isinstance(value, etree_element):
            value = value.text
        if value in ('False', '0', 'false'):
            value = False
        else:
            value = bool(value)
        return value

    def to_xml(self, value, tag):
        node = super(BooleanField, self).to_xml(value, tag)
        if value is not None:
            node.text = str(value).lower()
        return node

class IntegerField(Field):
    default_error_messages = {
        'invalid': 'Enter a whole number.',
    }
    default_xml_attributes = {
        'type': 'integer',
    }
    
    def to_python(self, value):
        if isinstance(value, etree_element):
            value = value.text
        try:
            value = int(str(value))
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'])
        return value
    
    def to_xml(self, value, tag):
        node = super(IntegerField, self).to_xml(value, tag)
        if value is not None:
            node.text = str(value)
        return node

class DecimalField(Field):
    default_error_messages = {
        'invalid': 'Enter a number.',
    }
    default_xml_attributes = {
        'type': 'decimal',
    }
    

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values.
        """
        if isinstance(value, etree_element):
            value = value.text
        if value in EMPTY_VALUES:
            return None
        value = str(value).strip()
        try:
            value = Decimal(value)
        except DecimalException:
            raise ValidationError(self.error_messages['invalid'])
        return value
    
    def to_xml(self, value, tag):
        node = super(DecimalField, self).to_xml(value, tag)
        if value is not None:
            node.text = str(value)
        return node


class FloatField(Field):
    default_error_messages = {
        'invalid': 'Enter a number.',
    }
    default_xml_attributes = {
        'type': 'float',
    }

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values.
        """
        if isinstance(value, etree_element):
            value = value.text
        if value in EMPTY_VALUES:
            return None
        try:
            value = str(value).strip()
            value = float(value)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])
        else:
            return value

    def to_xml(self, value, tag):
        node = super(FloatField, self).to_xml(value, tag)
        if value is not None:
            node.text = str(value)
        return node

class DateTimeField(Field):
    SHOPIFY_FORMAT = re.compile(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([-+])(\d{2}):(\d{2})')
    default_error_messages = {
        'invalid': 'Enter a valid date/time.',
    }
    default_xml_attributes = {
        'type': 'datetime',
    }
    
    def to_python(self, value):
        if isinstance(value, etree_element):
            value = value.text
        try:
            if value is None:
                return None
            elif isinstance(value, (str, unicode)):
                return dateutil.parser.parse(value)
            elif isinstance(value, datetime):
                return value
            elif isinstance(value, date):
                return datetime(value.year, value.month, value.day)
        except (ValueError, TypeError):
            pass
        raise ValidationError(self.error_messages['invalid'])
    
    def to_xml(self, value, tag):
        node = super(DateTimeField, self).to_xml(value, tag)
        if value is not None:
            value = value.strftime("%Y-%m-%dT%H:%M:%S%z")
            value = value[:-2] + ':' + value[-2:]
            node.text = value
        return node

class ElementField(Field):
    def __init__(self, element_class, *args, **kwargs):
        self.element_class  = element_class
        super(ElementField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        from shopipy.data.models import ShopifyElement
        if isinstance(value, ShopifyElement):
            return value
        
        # Get XML element
        node = None
        if isinstance(value, etree_element):
            node = value
        elif isinstance(value, (str, unicode)):
            node = etree.parse(value)
        else:
            raise ValueError("Could not parse XML from value: %s" % repr(value))
        
        # Parse XML element
        value = self.element_class.parse_xml(node)
        
        return value
    
    def to_xml(self, value, tag):
        return value.to_xml(tag)

class ArrayField(Field):
    def __init__(self, element_class, *args, **kwargs):
        self.child_xml_name = kwargs.pop('child_xml_name', None)
        self.element_class  = element_class
        super(ArrayField, self).__init__(*args, **kwargs)
    
    def to_python(self, value):
        # Get XML element
        node = None
        if isinstance(value, etree_element):
            node = value
        elif isinstance(value, (str, unicode)):
            node = etree.parse(value)
        elif isinstance(value, (tuple, list)):
            return value
        else:
            raise ValueError("Could not parse XML from value: %s" % repr(value))
        
        # Parse XML element
        arr = []
        for child in node:
            if child.tag == self.child_xml_name:
                arr.append(self.element_class.parse_xml(child))
        
        return arr
    
    def to_xml(self, value, tag):
        node = super(ArrayField, self).to_xml(value, tag)
        for child in value:
            node.append(child.to_xml(self.child_xml_name))
        return node

