import urllib
import urllib2

from shopipy.util import generate_url, generate_request, parse_xml, serialize_xml

class Shopify(object):
    def __init__(self, domain, api_key, password, secure=False):
        self.protocol = "https" if secure else "http"
        self.domain = domain
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm="Shopify API Authentication",
                                  uri=generate_url(self.protocol, self.domain, '/admin/', {}),
                                  user=api_key,
                                  passwd=password)
        self.urlopener = urllib2.build_opener(auth_handler)
    
    def _request(self, method, path, get_params, body=None, headers={}):
        url = generate_url(self.protocol, self.domain, path, get_params)
        request = generate_request(method, url, body)
        for name, value in headers.items():
            request.add_header(name, value)
        conn = self.urlopener.open(request)
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

