import os
import select
import socket
import ssl
import sys
import traceback

HOST = "127.0.0.1"
PORT = 8912


def sslProtocolVersion():
    # sslProtocolVersion
    if sys.version_info >= (2, 7, 13):
        # this means TLSv1 or higher
        # in the future change to
        # ssl.PROTOCOL_TLS1.2
        return ssl.PROTOCOL_TLS
    elif sys.version_info >= (2, 7, 9):
        # this means any SSL/TLS. SSLv2 and 3 are excluded with an option after context is created
        return ssl.PROTOCOL_SSLv23
    else:
        # this means TLSv1, there is no way to set "TLSv1 or higher" or
        # "TLSv1.2" in < 2.7.9
        return ssl.PROTOCOL_TLSv1


def sslProtocolCiphers():
    if ssl.OPENSSL_VERSION_NUMBER >= 0x10100000:
        return "AECDH-AES256-SHA@SECLEVEL=0"
    else:
        return "AECDH-AES256-SHA"


def connect():
    sock = socket.create_connection((HOST, PORT))
    return sock


def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(0)
    return sock


def sslHandshake(sock, server=False):
    if sys.version_info >= (2, 7, 9):
        context = ssl.SSLContext(sslProtocolVersion())
        context.set_ciphers(sslProtocolCiphers())
        context.set_ecdh_curve("secp256k1")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        context.options = ssl.OP_ALL | ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_SINGLE_ECDH_USE | ssl.OP_CIPHER_SERVER_PREFERENCE
        sslSock = context.wrap_socket(sock, server_side=server, do_handshake_on_connect=False)
    else:
        sslSock = ssl.wrap_socket(sock, keyfile=os.path.join('src', 'sslkeys', 'key.pem'),
                                  certfile=os.path.join('src', 'sslkeys', 'cert.pem'),
                                  server_side=server, ssl_version=sslProtocolVersion(),
                                  do_handshake_on_connect=False, ciphers='AECDH-AES256-SHA')

    while True:
        try:
            sslSock.do_handshake()
            break
        except ssl.SSLWantReadError:
            print "Waiting for SSL socket handhake read"
            select.select([sslSock], [], [], 10)
        except ssl.SSLWantWriteError:
            print "Waiting for SSL socket handhake write"
            select.select([], [sslSock], [], 10)
        except Exception:
            print "SSL socket handhake failed, shutting down connection"
            traceback.print_exc()
            return
    print "Success!"
    return sslSock


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: ssltest.py client|server"
        sys.exit(0)
    elif sys.argv[1] == "server":
        serversock = listen()
        while True:
            print "Waiting for connection"
            sock, addr = serversock.accept()
            print "Got connection from %s:%i" % (addr[0], addr[1])
            sslSock = sslHandshake(sock, True)
            if sslSock:
                sslSock.shutdown(socket.SHUT_RDWR)
                sslSock.close()
    elif sys.argv[1] == "client":
        sock = connect()
        sslSock = sslHandshake(sock, False)
        if sslSock:
            sslSock.shutdown(socket.SHUT_RDWR)
            sslSock.close()
    else:
        print "Usage: ssltest.py client|server"
        sys.exit(0)
