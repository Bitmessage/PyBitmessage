Encryption
==========

Bitmessage uses the Elliptic Curve Integrated Encryption Scheme
`(ECIES) <http://en.wikipedia.org/wiki/Integrated_Encryption_Scheme>`_
to encrypt the payload of the Message and Broadcast objects.

The scheme uses Elliptic Curve Diffie-Hellman
`(ECDH) <http://en.wikipedia.org/wiki/ECDH>`_ to generate a shared secret used
to generate the encryption parameters for Advanced Encryption Standard with
256bit key and Cipher-Block Chaining
`(AES-256-CBC) <http://en.wikipedia.org/wiki/Advanced_Encryption_Standard>`_.
The encrypted data will be padded to a 16 byte boundary in accordance to
`PKCS7 <http://en.wikipedia.org/wiki/Cryptographic_Message_Syntax>`_. This
means that the data is padded with N bytes of value N.

The Key Derivation Function
`(KDF) <http://en.wikipedia.org/wiki/Key_derivation_function>`_ used to
generate the key material for AES is
`SHA512 <http://en.wikipedia.org/wiki/Sha512>`_. The Message Authentication
Code (MAC) scheme used is `HMACSHA256 <http://en.wikipedia.org/wiki/Hmac>`_.

Format
------

(See also: :doc:`protocol`)

.. include:: encrypted_payload.rst

In order to reconstitute a usable (65 byte) public key (starting with 0x04),
the X and Y components need to be expanded by prepending them with 0x00 bytes
until the individual component lengths are 32 bytes.

Encryption
----------

 1. The destination public key is called K.
 2. Generate 16 random bytes using a secure random number generator.
    Call them IV.
 3. Generate a new random EC key pair with private key called r and public key
    called R.
 4. Do an EC point multiply with public key K and private key r. This gives you
    public key P.
 5. Use the X component of public key P and calculate the SHA512 hash H.
 6. The first 32 bytes of H are called key_e and the last 32 bytes are called
    key_m.
 7. Pad the input text to a multiple of 16 bytes, in accordance to PKCS7.
 8. Encrypt the data with AES-256-CBC, using IV as initialization vector,
    key_e as encryption key and the padded input text as payload. Call the
    output cipher text.
 9. Calculate a 32 byte MAC with HMACSHA256, using key_m as salt and
    IV + R + cipher text as data. Call the output MAC.

The resulting data is: IV + R + cipher text + MAC

Decryption
----------

 1. The private key used to decrypt is called k.
 2. Do an EC point multiply with private key k and public key R. This gives you
    public key P.
 3. Use the X component of public key P and calculate the SHA512 hash H.
 4. The first 32 bytes of H are called key_e and the last 32 bytes are called
    key_m.
 5. Calculate MAC' with HMACSHA256, using key_m as salt and
    IV + R + cipher text as data.
 6. Compare MAC with MAC'. If not equal, decryption will fail.
 7. Decrypt the cipher text with AES-256-CBC, using IV as initialization
    vector, key_e as decryption key and the cipher text as payload. The output
    is the padded input text.

.. highlight:: nasm

Partial Example
---------------

.. list-table:: Public key K:
   :header-rows: 1
   :widths: auto

   * - Data
     - Comments
   * -

       ::

          04 09 d4 e5  c0 ab 3d 25
          fe 04 8c 64  c9 da 1a 24
          2c 7f 19 41  7e 95 17 cd
          26 69 50 d7  2c 75 57 13
          58 5c 61 78  e9 7f e0 92
          fc 89 7c 9a  1f 17 20 d5
          77 0a e8 ea  ad 2f a8 fc
          bd 08 e9 32  4a 5d de 18
          57
     - Public key, 0x04 prefix, then 32 bytes X and 32 bytes Y.


.. list-table:: Initialization Vector IV:
   :header-rows: 1
   :widths: auto

   * - Data
     - Comments
   * -

       ::

	  bd db 7c 28  29 b0 80 38
	  75 30 84 a2  f3 99 16 81
     - 16 bytes generated with a secure random number generator.

.. list-table:: Randomly generated key pair with private key r and public key R:
   :header-rows: 1
   :widths: auto

   * - Data
     - Comments
   * -

       ::

	  5b e6 fa cd  94 1b 76 e9
	  d3 ea d0 30  29 fb db 6b
	  6e 08 09 29  3f 7f b1 97
	  d0 c5 1f 84  e9 6b 8b a4
     - Private key r
   * -

       ::

	  04 02 93 21  3d cf 13 88
	  b6 1c 2a e5  cf 80 fe e6
	  ff ff c0 49  a2 f9 fe 73
	  65 fe 38 67  81 3c a8 12
	  92 df 94 68  6c 6a fb 56
	  5a c6 14 9b  15 3d 61 b3
	  b2 87 ee 2c  7f 99 7c 14
	  23 87 96 c1  2b 43 a3 86
	  5a
     - Public key R

.. list-table:: Derived public key P (point multiply r with K):
   :header-rows: 1
   :widths: auto

   * - Data
     - Comments
   * -

       ::

	  04 0d b8 e3  ad 8c 0c d7
	  3f a2 b3 46  71 b7 b2 47
	  72 9b 10 11  41 57 9d 19
	  9e 0d c0 bd  02 4e ae fd
	  89 ca c8 f5  28 dc 90 b6
	  68 11 ab ac  51 7d 74 97
	  be 52 92 93  12 29 be 0b
	  74 3e 05 03  f4 43 c3 d2
	  96
     - Public key P
   * -

       ::

	  0d b8 e3 ad  8c 0c d7 3f
	  a2 b3 46 71  b7 b2 47 72
	  9b 10 11 41  57 9d 19 9e
	  0d c0 bd 02  4e ae fd 89
     - X component of public key P

.. list-table:: SHA512 of public key P X component (H):
   :header-rows: 1
   :widths: auto

   * - Data
     - Comments
   * -

       ::

	  17 05 43 82  82 67 86 71
	  05 26 3d 48  28 ef ff 82
	  d9 d5 9c bf  08 74 3b 69
	  6b cc 5d 69  fa 18 97 b4
     - First 32 bytes of H called key_e
   * -

       ::

	  f8 3f 1e 9c  c5 d6 b8 44
	  8d 39 dc 6a  9d 5f 5b 7f
	  46 0e 4a 78  e9 28 6e e8
	  d9 1c e1 66  0a 53 ea cd
     - Last 32 bytes of H called key_m

.. list-table:: Padded input:
   :header-rows: 1
   :widths: auto

   * - Data
     - Comments
   * -

       ::

	  54 68 65 20  71 75 69 63
	  6b 20 62 72  6f 77 6e 20
	  66 6f 78 20  6a 75 6d 70
	  73 20 6f 76  65 72 20 74
	  68 65 20 6c  61 7a 79 20
	  64 6f 67 2e  04 04 04 04
     - The quick brown fox jumps over the lazy dog.0x04,0x04,0x04,0x04

.. list-table:: Cipher text:
   :header-rows: 1
   :widths: auto

   * - Data
     - Comments
   * -

       ::

	  64 20 3d 5b  24 68 8e 25
	  47 bb a3 45  fa 13 9a 5a
	  1d 96 22 20  d4 d4 8a 0c
	  f3 b1 57 2c  0d 95 b6 16
	  43 a6 f9 a0  d7 5a f7 ea
	  cc 1b d9 57  14 7b f7 23
     - 3 blocks of 16 bytes of encrypted data.
