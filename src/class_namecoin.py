from jsonrpc import ServiceProxy, JSONRPCException

# This class handles the Namecoin identity integration.

class namecoinConnection(object):

    def __init__(self):
        user = "daniel"
        password = "password"
        host = "localhost"
        port = "8336"
        self.s = ServiceProxy ("http://" + user + ":" + password
                               + "@" + host + ":" + port)

    # Query for the bitmessage address corresponding to the given identity
    # string.  If it doesn't contain a slash, id/ is prepended.  We return
    # the result as (Error, Address) pair, where the Error is an error
    # message to display or None in case of success.
    def query(self,string):
        return None, "BM-Foobar2"
