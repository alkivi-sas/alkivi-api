"""
Helpers to ease calls on OVH api
"""

class PCA:
    """
    This class is used to ease access to pca file and data
    """

    def __init__(self, api, service_name, pca_service_name):
        self.api = api
        self.service_name = service_name
        self.pca_service_name = pca_service_name

    def get_sessions(self):
        """Return array of sessions id
        """
        url = '/cloud/%s/pca/%s/sessions' % (self.service_name, self.pca_service_name)
        return self.api.get(url)

    def get_session(self, session_id):
        """Get session infomration
        """
        url = '/cloud/%s/pca/%s/sessions/%s' % (self.service_name, self.pca_service_name, session_id)
        return self.api.get(url)

    def get_files(self, session_id):
        """Get id of files in session
        """
        url = '/cloud/%s/pca/%s/sessions/%s/files' % (self.service_name, self.pca_service_name, session_id)
        return self.api.get(url)

    def get_file(self, session_id, file_id):
        """Get file specific data
        """
        url = '/cloud/%s/pca/%s/sessions/%s/files/%s' % (self.service_name, self.pca_service_name, session_id, file_id)
        return self.api.get(url)

