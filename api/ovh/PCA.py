class OVH_PCA:
    """
    This class is used to ease access to pca file and data
    """
    def __init__(self, api, serviceName, pcaServiceName):
        self.api            = api
        self.serviceName    = serviceName
        self.pcaServiceName = pcaServiceName

    def getSessions(self):
        return self.api.get('/cloud/'+self.serviceName+'/pca/'+self.pcaServiceName+'/sessions')

    def getSession(self, session_id):
        return self.api.get('/cloud/'+self.serviceName+'/pca/'+self.pcaServiceName+'/sessions/'+session_id)

    def getFiles(self, session_id):
        return self.api.get('/cloud/'+self.serviceName+'/pca/'+self.pcaServiceName+'/sessions/'+session_id+'/files')

    def getFile(self, session_id, file_id):
        return self.api.get('/cloud/'+self.serviceName+'/pca/'+self.pcaServiceName+'/sessions/'+session_id+'/files/'+file_id)

