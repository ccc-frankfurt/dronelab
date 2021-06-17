import requests
import html
import google.cloud.storage


class getRequest:
    '''
        Class to send GET request
    '''

    def __init__(self, GET_URL = None, GET_PARAMS = None):
        if GET_PARAMS is not None:
            setParams(GET_PARAMS)
        else:
            self.GET_PARAMS = GET_PARAMS

        if GET_URL is not None:
            setUrl(GET_URL)
        else:
            self.GET_URL = None

    def setUrl(self, GET_URL):
        self.GET_URL = GET_URL

    def setParams(self, GET_PARAMS):
        self.GET_PARAMS = dict(GET_PARAMS)

    def makeRequest(self):
        self.request = requests.get(url = self.GET_URL, params = self.GET_PARAMS)
        try:
            self.response = self.request.json()
        except:
            self.response = "Error while extracting JSON response for the GET request, please check 'request' attribute for further details"





class postRequest:
    '''
        Class to send POST request
    '''

    def __init__(self, POST_URL = None, POST_PARAMS = None):
        if POST_PARAMS is not None:
            setParams(POST_PARAMS)
        else:
            self.POST_PARAMS = POST_PARAMS

        if POST_URL is not None:
            setUrl(POST_URL)
        else:
            self.POST_URL = None

    def setUrl(self, POST_URL):
        self.POST_URL = POST_URL

    def setParams(self, POST_PARAMS):
        self.POST_PARAMS = dict(POST_PARAMS)

    def makeRequest(self):
        self.request = requests.post(url = self.POST_URL, data = self.POST_PARAMS)
        try:
            self.response = self.request.json()
        except:
            self.response = "Error while extracting JSON response for the POST request, please check 'request' attribute for further details"




class uploadImageGC:
    '''
        Uploads Image to Google Cloud
    '''

    def __init__(self, service_account_json_file=None, bucket=None, source_file_path = None, destination_file_path = None):
        self.service_account_json_file = service_account_json_file
        self.bucket = bucket
        self.storage_client = None
        self.source_file_path = source_file_path
        self.destination_file_path = destination_file_path
        self.UPLOAD_URL = None

        if self.service_account_json_file is not None:
            makeStorageClient(self.service_account_json_file)

    def makeStorageClient(self, service_account_json_file):
        self.storage_client = google.cloud.storage.Client.from_service_account_json(service_account_json_emp)
        if self.bucket is not None:
            getBucket(self.bucket)


    def getBucket(self, bucket):
        if self.storage_client is not None:
            self.bucket = self.storage_client.get_bucket(bucket)
            if self.source_file_path is not None and self.destination_file_path is not None:
                uploadImage(self.source_file_path, self.destination_file_path)
        
        else:
            print("Storage client is currently None, bucket cannot be extracted for None client")

    def uploadImage(self, source_file_path, destination_file_path):

        try:
            blob = self.bucket.blob(destination_file_path)
            blob.upload_from_filename(source_file_path)
            blob.make_public()

            self.UPLOAD_URL = html.unescape(self.bucket.blob(destination_file_path).public_url)

        except Exception as e:
            print("Error Uploading Image to Google Cloud")
            print(e)






















