import urllib
import urllib2
import urlparse

__all__ = ['generate_url', 'generate_request', 'parse_xml', 'serialize_xml']

def _import_etree(packages=('lxml.etree', 'xml.etree.cElementTree',
                            'cElementTree', 'elementtree.ElementTree')):
    for pkg_name in packages:
        try:
            pkg = __import__(pkg_name)
        except ImportError:
            continue
        else:
            for subpkg_name in pkg_name.split('.')[1:]:  # skip the base package
                assert hasattr(pkg, subpkg_name)
                pkg = getattr(pkg, subpkg_name)
            return pkg
    raise ImportError("ElementTree library could not be found")

etree = _import_etree()

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
