import pyelliptic
from pyelliptic import arithmetic as a
def makeCryptor(privkey):
  privkey_bin = '\x02\xca\x00 '+a.changebase(privkey,16,256,minlen=32)
  pubkey = a.changebase(a.privtopub(privkey),16,256,minlen=65)[1:]
  pubkey_bin = '\x02\xca\x00 '+pubkey[:32]+'\x00 '+pubkey[32:]
  cryptor = pyelliptic.ECC(curve='secp256k1',privkey=privkey_bin,pubkey=pubkey_bin)
  return cryptor
def hexToPubkey(pubkey):
  pubkey_raw = a.changebase(pubkey[2:],16,256,minlen=64)
  pubkey_bin = '\x02\xca\x00 '+pubkey_raw[:32]+'\x00 '+pubkey_raw[32:]
  return pubkey_bin
def makePubCryptor(pubkey):
  pubkey_bin = hexToPubkey(pubkey)
  return pyelliptic.ECC(curve='secp256k1',pubkey=pubkey_bin)
# Converts hex private key into hex public key
def privToPub(privkey):
  return a.privtopub(privkey)
# Encrypts message with hex public key
def encrypt(msg,hexPubkey):
  return pyelliptic.ECC(curve='secp256k1').encrypt(msg,hexToPubkey(hexPubkey))
# Decrypts message with hex private key
def decrypt(msg,hexPrivkey):
  return makeCryptor(hexPrivkey).decrypt(msg)
# Decrypts message with an existing pyelliptic.ECC.ECC object
def decryptFast(msg,cryptor):
  return cryptor.decrypt(msg)
# Signs with hex private key
def sign(msg,hexPrivkey):
  return makeCryptor(hexPrivkey).sign(msg)
# Verifies with hex public key
def verify(msg,sig,hexPubkey):
  return makePubCryptor(hexPubkey).verify(sig,msg)
