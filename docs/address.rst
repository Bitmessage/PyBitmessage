Address
=======

Bitmessage adresses are Base58 encoded public key hashes. An address looks like
``BM-BcbRqcFFSQUUmXFKsPJgVQPSiFA3Xash``. All Addresses start with ``BM-``,
however clients should accept addresses without the prefix. PyBitmessage does
this. The reason behind this idea is the fact, that when double clicking on an
address for copy and paste, the prefix is usually not selected due to the dash
being a common separator.

Public Key usage
----------------

Addresses may look complicated but they fulfill the purpose of verifying the
sender. A Message claiming to be from a specific address can simply be checked by
decoding a special field in the data packet with the public key, that represents
the address. If the decryption succeeds, the message is from the address it
claims to be.

Length
------

Without the ``BM-`` prefix, an address is usually 32-34 chars long. Since an
address is a hash it can be calculated by the client in a way, that the first
bytes are zero (``\0``) and bitmessage strips these. This causes the client to do
much more work to be lucky and find such an address. This is an optional checkbox
in address generation dialog.

Versions
--------

 * v1 addresses used a single RSA key pair
 * v2 addresses use 2 ECC key pairs
 * v3 addresses extends v2 addresses to allow specifying the proof of work
   requirements. The pubkey object is signed to mitigate against
   forgery/tampering.
 * v4 addresses protect against harvesting addresses from getpubkey and pubkey
   objects

Address Types
-------------

There are two address types the user can generate in PyBitmessage. The resulting
addresses have no difference, but the method how they are created differs.

Random Address
^^^^^^^^^^^^^^

Random addresses are generated from a randomly chosen number. The resulting
address cannot be regenerated without knowledge of the number and therefore the
keys.dat should be backed up. Generating random addresses takes slightly longer
due to the POW required for the public key broadcast.

Usage
"""""

 * Generate unique addresses
 * Generate one time addresses.


Deterministic Address
^^^^^^^^^^^^^^^^^^^^^

For this type of Address a passphrase is required, that is used to seed the
random generator. Using the same passphrase creates the same addresses.
Using deterministic addresses should be done with caution, using a word from a
dictionary or a common number can lead to others generating the same address and
thus being able to receive messages not intended for them. Generating a
deterministic address will not publish the public key. The key is sent in case
somebody requests it. This saves :doc:`pow` time, when generating a bunch of
addresses.

Usage
"""""

 * Create the same address on multiple systems without the need of copying
   keys.dat or an Address Block.
 * create a Channel. (Use the *Join/create chan* option in the file menu instead)
 * Being able to restore the address in case of address database corruption or
   deletation.

Address generation
------------------

 1. Create a private and a public key for encryption and signing (resulting in
    4 keys)
 2. Merge the public part of the signing key and the encryption key together.
    (encoded in uncompressed X9.62 format) (A)
 3. Take the SHA512 hash of A. (B)
 4. Take the RIPEMD160 of B. (C)
 5. Repeat step 1-4 until you have a result that starts with a zero
    (Or two zeros, if you want a short address). (D)
 6. Remove the zeros at the beginning of D. (E)
 7. Put the stream number (as a var_int) in front of E. (F)
 8. Put the address version (as a var_int) in front of F. (G)
 9. Take a double SHA512 (hash of a hash) of G and use the first four bytes as a
    checksum, that you append to the end. (H)
 10. base58 encode H. (J)
 11. Put "BM-" in front J. (K)

K is your full address

 .. note:: Bitmessage's base58 encoding uses the following sequence
	   (the same as Bitcoin's):
	   "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz".
	   Many existing libraries for base58 do not use this ordering.
