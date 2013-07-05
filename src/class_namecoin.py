import json
from jsonrpc import ServiceProxy, JSONRPCException

# This class handles the Namecoin identity integration.

class namecoinConnection(object):

    def __init__(self):
        user = "daniel"
        password = "password"
        host = "localhost"
        port = "8336"
        self.s = ServiceProxy("http://" + user + ":" + password
                              + "@" + host + ":" + port)

    # Query for the bitmessage address corresponding to the given identity
    # string.  If it doesn't contain a slash, id/ is prepended.  We return
    # the result as (Error, Address) pair, where the Error is an error
    # message to display or None in case of success.
    def query(self,string):
        slashPos = string.find("/")
        if slashPos < 0:
            string = "id/" + string

        try:
            res = self.s.name_show(string)
        except JSONRPCException as err:
            if err.error["code"] == -4:
                return ("The name '" + string + "' was not found.", None)
            else:
                return ("The namecoin query failed ("
                        + err.error["message"] + ")", None)
        except:
            return ("The namecoin query failed.", None)

        try:
            print res["value"]
            val = json.loads(res["value"])
        except:
            return ("The name '" + string + "' has no valid JSON data.", None)

        if "bitmessage" in val:
            return (None, val["bitmessage"])

        return ("The name '" + string
                + "' has no associated Bitmessage address.", None)
