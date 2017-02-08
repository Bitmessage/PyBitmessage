# sanity check, prevent doing ridiculous PoW
# 20 million PoWs equals approximately 2 days on dev's dual R9 290
ridiculousDifficulty = 20000000

# Remember here the RPC port read from namecoin.conf so we can restore to
# it as default whenever the user changes the "method" selection for
# namecoin integration to "namecoind".
namecoinDefaultRpcPort = "8336"
