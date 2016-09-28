__author__ = 'bcarson'

import requests
import io

class ImageSource(object):

    def __init__(self, download_url, username, password):
        self.download_url = download_url

        if username is not None:
            self.authorisation = (username, password)
        else:
            self.authorisation = None

    def get_image(self):
        try:
            request = requests.get(self.download_url, auth=self.authorisation)

            if request.status_code is 200:
                return io.BytesIO(request.content)

        except requests.ConnectionError, e:
            print "Connection Error:", e, request
        except requests.HTTPError, e:
            print "HTTP Error:", e, request

        return None
