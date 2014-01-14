"""
Helpers to ease calls on OVH api
"""

class Me:
    """
    This class is used to ease access to bills ...
    """

    def __init__(self, api):
        self.api = api

    def get_my_info(self):
        """Fetch info for my nic
        """
        return self.api.get('/me')

    def get_bills(self, from_date=None, to_date=None):
        """Return array of bills
        """
        params = {}
        if(from_date):
            params['date.from'] = from_date

        if(to_date):
            params['date.to'] = to_date
        return self.api.get('/me/bill', params)

    def get_bill(self, bill_id):
        """Return bill specifics
        """
        return self.api.get('/me/bill/'+bill_id)

    def get_bill_details(self, bill_id):
        """Return array of bill details
        """
        return self.api.get('/me/bill/'+bill_id+'/details')

    def get_bill_payment(self, bill_id):
        """Return bill payment
        """
        return self.api.get('/me/bill/'+bill_id+'/payment')

    def get_bill_detail(self, bill_id, detail_id):
        """Return specific bill payment
        """
        return self.api.get('/me/bill/'+bill_id+'/details/'+detail_id)


