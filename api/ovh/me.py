from alkivi.common.logger import Logger

class OVH_Me:
    """
    This class is used to ease access to bills ...
    """
    def __init__(self, api):
        self.api            = api

    def getMyInfo(self):
        return self.api.get('/me')

    def getBills(self, fromDate=None, toDate=None):
        params = {}
        if(fromDate):
            params['date.from'] = fromDate

        if(toDate):
            params['date.to'] = toDate
        return self.api.get('/me/bill', params)

    def getBill(self, bill_id):
        return self.api.get('/me/bill/'+bill_id)

    def getBillDetails(self, bill_id):
        return self.api.get('/me/bill/'+bill_id+'/details')

    def getBillPayment(self, bill_id):
        return self.api.get('/me/bill/'+bill_id+'/payment')

    def getBillDetail(self, bill_id, detail_id):
        return self.api.get('/me/bill/'+bill_id+'/details/'+detail_id)


