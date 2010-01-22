import urllib
import urllib2
import urlparse

try:
  from lxml import etree
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
      except ImportError:
          # normal ElementTree install
          import elementtree.ElementTree as etree

def generate_url(protocol, domain, path, param_dict):
    url = "%s://%s%s" % (protocol, domain, path)
    if len(param_dict) > 0:
        return urlparse.urljoin(url, '?' + urllib.urlencode(param_dict))
    else:
        return url

def generate_request(action, url, body=None):
    assert action.upper() in ('GET', 'DELETE') and body is None or \
           action.upper() in ('POST', 'PUT')

    request = urllib2.Request(url, data=body)
    request.get_method = lambda: action
    return request

def parse_xml(obj):
    return etree.parse(obj).getroot()

def serialize_xml(obj):
    return etree.tostring(obj)
