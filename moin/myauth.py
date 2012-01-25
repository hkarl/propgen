# -*- coding: iso-8859-1 -*-

from MoinMoin import log
logging = log.getLogger(__name__)

from MoinMoin.auth import BaseAuth, GivenAuth, MoinAuth
from MoinMoin import user, wikiutil

class MyAuth(MoinAuth):
    """ handle login from moin login form """
     
    def login_hint(self, request):
        _ = request.getText
        #userprefslink = request.page.url(request, querystr={'action': 'newaccount'})
        sendmypasswordlink = request.page.url(request, querystr={'action': 'recoverpass'})
        return _('<a href="%(sendmypasswordlink)s">Password vergessen?</a>') % {
               'sendmypasswordlink': sendmypasswordlink}
     

