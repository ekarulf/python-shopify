import base64
import urllib
import urllib2
import platform
import shopipy

from shopipy.util import generate_url, generate_request, parse_xml, serialize_xml

class Shopify(object):
    DEFAULT_HEADERS = {
        'User-Agent':   'Shopipy/%s Python/%s %s/%s' % (shopipy.__version__, platform.python_version(), platform.system(), platform.release()),
    }
    
    def __init__(self, domain, api_key, password, secure=True, api_throttle=None):
        self.protocol = "https" if secure else "http"
        self.domain = domain
        self.api_key = api_key
        self.api_throttle = api_throttle
        # HTTPBasicAuthHandler does not reliably set this header in Python 2.7
        # Originally, this code used a urllib2 urlopener.
        self.headers = dict(self.DEFAULT_HEADERS, **{
            "Authorization": "Basic %s" % base64.b64encode(":".join((api_key, password))),
        })
    
    def _request(self, method, path, get_params, body=None, headers={}):
        # Allow API throttling via various mechanisms
        if callable(self.api_throttle):
            self.api_throttle(self)
        
        # Create and send HTTP Request
        url = generate_url(self.protocol, self.domain, path, get_params)
        req_headers = dict(self.headers, **headers)
        request = generate_request(method, url, body)
        for name, value in req_headers.items():
            request.add_header(name, value)
        conn = urllib2.urlopen(request)
        
        # Parse HTTP Response (expecting a well-formed XML document)
        root = parse_xml(conn)
        return root
    
    def GET(self, path, **kwargs):
        """
        Issues an authenticated GET request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        return self._request('GET', path, kwargs)
    
    def POST(self, path, body, **kwargs):
        """
        Issues an authenticated POST request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        return self._request('POST', path, kwargs, body, headers = {
            'Content-Type': 'text/xml',
        })
    
    def PUT(self, path, body, **kwargs):
        """
        Issues an authenticated PUT request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        return self._request('PUT', path, kwargs, body, headers = {
            'Content-Type': 'text/xml',
        })
    
    def DELETE(self, path, **kwargs):
        """
        Issues an authenticated DELETE request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        return self._request('DELETE', path, kwargs)

