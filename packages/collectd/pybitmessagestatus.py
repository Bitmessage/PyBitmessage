#!/usr/bin/env python2.7

import collectd
import json
import xmlrpclib

pybmurl = ""
api = ""

def init_callback():
    global api
    api = xmlrpclib.ServerProxy(pybmurl)
    collectd.info('pybitmessagestatus.py init done')

def config_callback(ObjConfiguration):
    global pybmurl
    apiUsername = ""
    apiPassword = ""
    apiInterface = "127.0.0.1"
    apiPort = 8445
    for node in ObjConfiguration.children:
        key = node.key.lower()
        if key.lower() == "apiusername" and node.values:
            apiUsername = node.values[0]
        elif key.lower() == "apipassword" and node.values:
            apiPassword = node.values[0]
        elif key.lower() == "apiinterface" and node.values:
            apiInterface = node.values[0]
        elif key.lower() == "apiport" and node.values:
            apiPort = node.values[0]
    pybmurl = "http://" + apiUsername + ":" + apiPassword + "@" + apiInterface+ ":" + str(int(apiPort)) + "/"
    collectd.info('pybitmessagestatus.py config done')

def read_callback():
    try:
        clientStatus = json.loads(api.clientStatus())
    except:
        collectd.info("Exception loading or parsing JSON")
        return

    for i in ["networkConnections", "numberOfPubkeysProcessed", "numberOfMessagesProcessed", "numberOfBroadcastsProcessed"]:
        metric = collectd.Values()
        metric.plugin = "pybitmessagestatus"
        if i[0:6] == "number":
            metric.type = 'counter'
        else:
            metric.type = 'gauge'
        metric.type_instance = i.lower()
        try:
            metric.values = [clientStatus[i]]
        except:
            collectd.info("Value for %s missing" % (i))
        metric.dispatch()

if __name__ == "__main__":
    main()
else:
    collectd.register_init(init_callback)
    collectd.register_config(config_callback)
    collectd.register_read(read_callback)
