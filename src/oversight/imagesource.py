__author__ = 'bcarson'

import urllib2, base64


class ImageSource(object):

    def __init__(self, download_url, username, password):
        self.download_url = download_url

        if username is not None:
            self.authorisation = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        else:
            self.authorisation = None

    def get_image(self):
        request = urllib2.Request(self.download_url)

        if self.authorisation is not None:
            request.add_header("Authorization", "Basic %s" % self.authorisation)

        try:
            return urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            print "HTTP Error:", e.code, request
        except urllib2.URLError, e:
            print "URL Error:", e.reason, request

        return None
