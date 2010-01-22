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
    
    def GET(self, path, **kwargs):
        """
        Issues an authenticated GET request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        url = generate_url(self.protocol, self.domain, path, kwargs)
        request = generate_request('GET', url)
        conn = self.urlopener.open(request)
        root = parse_xml(conn)
        return root
    
    def POST(self, path, body, **kwargs):
        """
        Issues an authenticated POST request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        url = generate_url(self.protocol, self.domain, path, kwargs)
        request = generate_request('POST', url, serialize_xml(body))
        request.add_header('Content-Type', 'text/xml')
        conn = self.urlopener.open(request)
        root = parse_xml(conn)
        return root
    
    def PUT(self, path, body, **kwargs):
        """
        Issues an authenticated PUT request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        url = generate_url(self.protocol, self.domain, path, kwargs)
        request = generate_request('PUT', url, serialize_xml(body))
        request.add_header('Content-Type', 'text/xml')
        conn = self.urlopener.open(request)
        root = parse_xml(conn)
        return root
    
    def DELETE(self, path, **kwargs):
        """
        Issues an authenticated DELETE request to the given path
        If present, any keyword arguments are converted to GET parameters
        @return root - ElementTree root
        """
        url = generate_url(self.protocol, self.domain, path, kwargs)
        request = generate_request('DELETE', url)
        conn = self.urlopener.open(request)
        root = parse_xml(conn)
        return root

