"""
Calculates bitcoin and testnet address from pubkey
"""

import hashlib
from fallback import RIPEMD160Hash
from debug import logger
from pyelliptic import arithmetic


def calculateBitcoinAddressFromPubkey(pubkey):
    """Calculate bitcoin address from given pubkey (65 bytes long hex string)"""
    if len(pubkey) != 65:
        logger.error('Could not calculate Bitcoin address from pubkey because'
                     ' function was passed a pubkey that was'
                     ' %i bytes long rather than 65.', len(pubkey))
        return "error"
    sha = hashlib.new('sha256')
    sha.update(pubkey)
    ripe = RIPEMD160Hash(sha.digest())
    ripeWithProdnetPrefix = b'\x00' + ripe.digest()

    checksum = hashlib.sha256(hashlib.sha256(
        ripeWithProdnetPrefix).digest()).digest()[:4]
    binaryBitcoinAddress = ripeWithProdnetPrefix + checksum
    numberOfZeroBytesOnBinaryBitcoinAddress = 0
    while binaryBitcoinAddress.startswith(b'\x00'):
        numberOfZeroBytesOnBinaryBitcoinAddress += 1
        binaryBitcoinAddress = binaryBitcoinAddress[1:]
    base58encoded = arithmetic.changebase(binaryBitcoinAddress, 256, 58)
    return b"1" * numberOfZeroBytesOnBinaryBitcoinAddress + base58encoded


def calculateTestnetAddressFromPubkey(pubkey):
    """This function expects that pubkey begin with the testnet prefix"""
    if len(pubkey) != 65:
        logger.error('Could not calculate Bitcoin address from pubkey because'
                     ' function was passed a pubkey that was'
                     ' %i bytes long rather than 65.', len(pubkey))
        return "error"
    sha = hashlib.new('sha256')
    sha.update(pubkey)
    ripe = RIPEMD160Hash(sha.digest())
    ripeWithProdnetPrefix = b'\x6F' + ripe.digest()

    checksum = hashlib.sha256(hashlib.sha256(
        ripeWithProdnetPrefix).digest()).digest()[:4]
    binaryBitcoinAddress = ripeWithProdnetPrefix + checksum
    numberOfZeroBytesOnBinaryBitcoinAddress = 0
    while binaryBitcoinAddress.startswith(b'\x00'):
        numberOfZeroBytesOnBinaryBitcoinAddress += 1
        binaryBitcoinAddress = binaryBitcoinAddress[1:]
    base58encoded = arithmetic.changebase(binaryBitcoinAddress, 256, 58)
    return b"1" * numberOfZeroBytesOnBinaryBitcoinAddress + base58encoded
