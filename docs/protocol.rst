Protocol specification
======================

.. warning:: All objects sent on the network should support protocol v3
	     starting on Sun, 16 Nov 2014 22:00:00 GMT.

.. toctree::
   :maxdepth: 2

Common standards
----------------

Hashes
^^^^^^

Most of the time `SHA-512 <http://en.wikipedia.org/wiki/SHA-2>`_ hashes are
used, however `RIPEMD-160 <http://en.wikipedia.org/wiki/RIPEMD>`_ is also used
when creating an address.

A double-round of SHA-512 is used for the Proof Of Work. Example of
double-SHA-512 encoding of string "hello":

.. highlight:: nasm

::

   hello
   9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043(first round of sha-512)
   0592a10584ffabf96539f3d780d776828c67da1ab5b169e9e8aed838aaecc9ed36d49ff1423c55f019e050c66c6324f53588be88894fef4dcffdb74b98e2b200(second round of sha-512)

For Bitmessage addresses (RIPEMD-160) this would give:

::

   hello
   9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043(first round is sha-512)
   79a324faeebcbf9849f310545ed531556882487e (with ripemd-160)


Common structures
-----------------

All integers are encoded in big endian. (This is different from Bitcoin).

.. list-table:: Message structure
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 4
     - magic
     - uint32_t
     - Magic value indicating message origin network, and used to seek to next
       message when stream state is unknown
   * - 12
     - command
     - char[12]
     - ASCII string identifying the packet content, NULL padded (non-NULL
       padding results in packet rejected)
   * - 4
     - length
     - uint32_t
     - Length of payload in number of bytes. Because of other restrictions,
       there is no reason why this length would ever be larger than 1600003
       bytes. Some clients include a sanity-check to avoid processing messages
       which are larger than this.
   * - 4
     - checksum
     - uint32_t
     - First 4 bytes of sha512(payload)
   * - ?
     - message_payload
     - uchar[]
     - The actual data, a :ref:`message <msg-types>` or an object_.
       Not to be confused with objectPayload.

Known magic values:

+-------------+-------------------+
| Magic value | Sent over wire as |
+=============+===================+
| 0xE9BEB4D9  | E9 BE B4 D9       |
+-------------+-------------------+

.. _varint:

Variable length integer
^^^^^^^^^^^^^^^^^^^^^^^

Integer can be encoded depending on the represented value to save space.
Variable length integers always precede an array/vector of a type of data that
may vary in length. Varints MUST use the minimum possible number of bytes to
encode a value. For example, the value 6 can be encoded with one byte therefore
a varint that uses three bytes to encode the value 6 is malformed and the
decoding task must be aborted.

+---------------+----------------+------------------------------------------+
| Value         | Storage length | Format                                   |
+===============+================+==========================================+
| < 0xfd        | 1              | uint8_t                                  |
+---------------+----------------+------------------------------------------+
| <= 0xffff     | 3              | 0xfd followed by the integer as uint16_t |
+---------------+----------------+------------------------------------------+
| <= 0xffffffff | 5              | 0xfe followed by the integer as uint32_t |
+---------------+----------------+------------------------------------------+
| -             | 9              | 0xff followed by the integer as uint64_t |
+---------------+----------------+------------------------------------------+

Variable length string
^^^^^^^^^^^^^^^^^^^^^^

Variable length string can be stored using a variable length integer followed by
the string itself.

+------------+-------------+------------+----------------------------------+
| Field Size | Description | Data type  | Comments                         |
+============+=============+============+==================================+
| 1+         | length      | |var_int|  | Length of the string             |
+------------+-------------+------------+----------------------------------+
| ?          | string      | char[]     | The string itself (can be empty) |
+------------+-------------+------------+----------------------------------+

Variable length list of integers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

n integers can be stored using n+1 :ref:`variable length integers <varint>`
where the first var_int equals n.

+------------+-------------+-----------+----------------------------+
| Field Size | Description | Data type | Comments                   |
+============+=============+===========+============================+
| 1+         | count       | |var_int| | Number of var_ints below   |
+------------+-------------+-----------+----------------------------+
| 1+         |             | var_int   | The first value stored     |
+------------+-------------+-----------+----------------------------+
| 1+         |             | var_int   | The second value stored... |
+------------+-------------+-----------+----------------------------+
| 1+         |             | var_int   | etc...                     |
+------------+-------------+-----------+----------------------------+

.. |var_int| replace:: :ref:`var_int <varint>`

Network address
^^^^^^^^^^^^^^^

When a network address is needed somewhere, this structure is used. Network
addresses are not prefixed with a timestamp or stream in the version_ message.

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 8
     - time
     - uint64
     - the Time.
   * - 4
     - stream
     - uint32
     - Stream number for this node
   * - 8
     - services
     - uint64_t
     - same service(s) listed in version_
   * - 16
     - IPv6/4
     - char[16]
     - IPv6 address. IPv4 addresses are written into the message as a 16 byte
       `IPv4-mapped IPv6 address <http://en.wikipedia.org/wiki/IPv6#IPv4-mapped_IPv6_addresses>`_
       (12 bytes 00 00 00 00 00 00 00 00 00 00 FF FF, followed by the 4 bytes of
       the IPv4 address).
   * - 2
     - port
     - uint16_t
     - port number

Inventory Vectors
^^^^^^^^^^^^^^^^^

Inventory vectors are used for notifying other nodes about objects they have or
data which is being requested. Two rounds of SHA-512 are used, resulting in a
64 byte hash. Only the first 32 bytes are used; the later 32 bytes are ignored.

Inventory vectors consist of the following data format:

+------------+-------------+-----------+--------------------+
| Field Size | Description | Data type | Comments           |
+============+=============+===========+====================+
| 32         | hash        | char[32]  | Hash of the object |
+------------+-------------+-----------+--------------------+

Encrypted payload
^^^^^^^^^^^^^^^^^

Bitmessage uses `ECIES <https://en.wikipedia.org/wiki/Integrated_Encryption_Scheme>`_ to encrypt its messages. For more information see :doc:`encryption`

.. include:: encrypted_payload.rst

Unencrypted Message Data
^^^^^^^^^^^^^^^^^^^^^^^^


Message Encodings
"""""""""""""""""

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Value
     - Name
     - Description
   * - 0
     - IGNORE
     - Any data with this number may be ignored. The sending node might simply
       be sharing its public key with you.
   * - 1
     - TRIVIAL
     - UTF-8. No 'Subject' or 'Body' sections. Useful for simple strings
       of data, like URIs or magnet links.
   * - 2
     - SIMPLE
     - UTF-8. Uses 'Subject' and 'Body' sections. No MIME is used.
       ::
	  messageToTransmit = 'Subject:' + subject + '\n' + 'Body:' + message
   * - 3
     - EXTENDED
     - See :doc:`extended_encoding`

Further values for the message encodings can be decided upon by the community.
Any MIME or MIME-like encoding format, should they be used, should make use of
Bitmessage's 8-bit bytes. 

Pubkey bitfield features
""""""""""""""""""""""""

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Bit
     - Name
     - Description
   * - 0
     - undefined
     - The most significant bit at the beginning of the structure. Undefined
   * - 1
     - undefined
     - The next most significant bit. Undefined
   * - ...
     - ...
     - ...
   * - 27
     - onion_router
     - (**Proposal**) Node can be used to onion-route messages. In theory any
       node can onion route, but since it requires more resources, they may have
       the functionality disabled. This field will be used to indicate that the
       node is willing to do this.
   * - 28
     - forward_secrecy
     - (**Proposal**) Receiving node supports a forward secrecy encryption
       extension. The exact design is pending.
   * - 29
     - chat
     - (**Proposal**) Address if for chatting rather than messaging.
   * - 30
     - include_destination
     - (**Proposal**) Receiving node expects that the RIPE hash encoded in their
       address preceedes the encrypted message data of msg messages bound for
       them.

       .. note:: since hardly anyone implements this, this will be redesigned as
		 `simple recipient verification <https://github.com/Bitmessage/PyBitmessage/pull/808#issuecomment-170189856>`_
   * - 31
     - does_ack
     - If true, the receiving node does send acknowledgements (rather than
       dropping them).

.. _msg-types:

Message types
-------------

Undefined messages received on the wire must be ignored.

version
^^^^^^^

When a node creates an outgoing connection, it will immediately advertise its
version. The remote node will respond with its version. No futher communication
is possible until both peers have exchanged their version.

.. list-table:: Payload
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 4
     - version
     - int32_t
     - Identifies protocol version being used by the node. Should equal 3.
       Nodes should disconnect if the remote node's version is lower but
       continue with the connection if it is higher.
   * - 8
     - services
     - uint64_t
     - bitfield of features to be enabled for this connection
   * - 8
     - timestamp
     - int64_t
     - standard UNIX timestamp in seconds
   * - 26
     - addr_recv
     - net_addr
     - The network address of the node receiving this message (not including the
       time or stream number)
   * - 26
     - addr_from
     - net_addr
     - The network address of the node emitting this message (not including the
       time or stream number and the ip itself is ignored by the receiver)
   * - 8
     - nonce
     - uint64_t
     - Random nonce used to detect connections to self.
   * - 1+
     - user_agent
     - var_str
     - :doc:`useragent` (0x00 if string is 0 bytes long). Sending nodes must not
       include a user_agent longer than 5000 bytes.
   * - 1+
     - stream_numbers
     - var_int_list
     - The stream numbers that the emitting node is interested in. Sending nodes
       must not include more than 160000 stream numbers.

A "verack" packet shall be sent if the version packet was accepted. Once you
have sent and received a verack messages with the remote node, send an addr
message advertising up to 1000 peers of which you are aware, and one or more
inv messages advertising all of the valid objects of which you are aware.

.. list-table:: The following services are currently assigned
   :header-rows: 1
   :widths: auto

   * - Value
     - Name
     - Description
   * - 1
     - NODE_NETWORK
     - This is a normal network node.
   * - 2
     - NODE_SSL
     - This node supports SSL/TLS in the current connect (python < 2.7.9 only
       supports a SSL client, so in that case it would only have this on when
       the connection is a client).
   * - 3
     - NODE_POW
     - (**Proposal**) This node may do PoW on behalf of some its peers (PoW
       offloading/delegating), but it doesn't have to. Clients may have to meet
       additional requirements (e.g. TLS authentication)
   * - 4
     - NODE_DANDELION
     - Node supports `dandelion <https://github.com/gfanti/bips/blob/master/bip-dandelion.mediawiki>`_

verack
^^^^^^

The verack message is sent in reply to version. This message consists of only a
message header with the command string "verack". The TCP timeout starts out at
20 seconds; after verack messages are exchanged, the timeout is raised to
10 minutes.

If both sides announce that they support SSL, they MUST perform a SSL handshake
immediately after they both send and receive verack. During this SSL handshake,
the TCP client acts as a SSL client, and the TCP server acts as a SSL server.
The current implementation (v0.5.4 or later) requires the AECDH-AES256-SHA
cipher over TLSv1 protocol, and prefers the secp256k1 curve (but other curves
may be accepted, depending on the version of python and OpenSSL used).

addr
^^^^

Provide information on known nodes of the network. Non-advertised nodes should
be forgotten after typically 3 hours

Payload:

+------------+-------------+-----------+---------------------------------------+
| Field Size | Description | Data type | Comments                              |
+============+=============+===========+=======================================+
| 1+         | count       | |var_int| | Number of address entries (max: 1000) |
+------------+-------------+-----------+---------------------------------------+
| 38         | addr_list   | net_addr  | Address of other nodes on the network.|
+------------+-------------+-----------+---------------------------------------+

inv
^^^

Allows a node to advertise its knowledge of one or more objects. Payload
(maximum payload length: 50000 items):

+------------+-------------+------------+-----------------------------+
| Field Size | Description | Data type  | Comments                    |
+============+=============+============+=============================+
| ?          | count       | |var_int|  | Number of inventory entries |
+------------+-------------+------------+-----------------------------+
| 32x?       | inventory   | inv_vect[] | Inventory vectors           |
+------------+-------------+------------+-----------------------------+


getdata
^^^^^^^

getdata is used in response to an inv message to retrieve the content of a
specific object after filtering known elements.

Payload (maximum payload length: 50000 entries):

+------------+-------------+------------+-----------------------------+
| Field Size | Description | Data type  | Comments                    |
+============+=============+============+=============================+
| ?          | count       | |var_int|  | Number of inventory entries |
+------------+-------------+------------+-----------------------------+
| 32x?       | inventory   | inv_vect[] | Inventory vectors           |
+------------+-------------+------------+-----------------------------+


object
^^^^^^

An object is a message which is shared throughout a stream. It is the only
message which propagates; all others are only between two nodes. Objects have a
type, like 'msg', or 'broadcast'. To be a valid object, the
:doc:`pow` must be done. The maximum allowable length of an object
(not to be confused with the ``objectPayload``) is |2^18| bytes.

.. |2^18| replace:: 2\ :sup:`18`\

.. list-table:: Message structure
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 8
     - nonce
     - uint64_t
     - Random nonce used for the :doc:`pow`
   * - 8
     - expiresTime
     - uint64_t
     - The "end of life" time of this object (be aware, in version 2 of the
       protocol this was the generation time). Objects shall be shared with
       peers until its end-of-life time has been reached. The node should store
       the inventory vector of that object for some extra period of time to
       avoid reloading it from another node with a small time delay. The time
       may be no further than 28 days + 3 hours in the future.
   * - 4
     - objectType
     - uint32_t
     - Four values are currently defined: 0-"getpubkey", 1-"pubkey", 2-"msg",
       3-"broadcast". All other values are reserved. Nodes should relay objects
       even if they use an undefined object type.
   * - 1+
     - version
     - var_int
     - The object's version. Note that msg objects won't contain a version
       until Sun, 16 Nov 2014 22:00:00 GMT.
   * - 1+
     - stream number
     - var_int
     - The stream number in which this object may propagate
   * - ?
     - objectPayload
     - uchar[]
     - This field varies depending on the object type; see below.


Object types
------------

Here are the payloads for various object types.

getpubkey
^^^^^^^^^

When a node has the hash of a public key (from an address) but not the public
key itself, it must send out a request for the public key.

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 20
     - ripe
     - uchar[]
     - The ripemd hash of the public key. This field is only included when the
       address version is <= 3.
   * - 32
     - tag
     - uchar[]
     - The tag derived from the address version, stream number, and ripe. This
       field is only included when the address version is >= 4.

pubkey
^^^^^^

A version 2 pubkey. This is still in use and supported by current clients but
*new* v2 addresses are not generated by clients.

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 4
     - behavior bitfield
     - uint32_t
     - A bitfield of optional behaviors and features that can be expected from
       the node receiving the message.
   * - 64
     - public signing key
     - uchar[]
     - The ECC public key used for signing (uncompressed format;
       normally prepended with \x04 )
   * - 64
     - public encryption key
     - uchar[]
     - The ECC public key used for encryption (uncompressed format;
       normally prepended with \x04 )

.. list-table:: A version 3 pubkey
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 4
     - behavior bitfield
     - uint32_t
     - A bitfield of optional behaviors and features that can be expected from
       the node receiving the message.
   * - 64
     - public signing key
     - uchar[]
     - The ECC public key used for signing (uncompressed format;
       normally prepended with \x04 )
   * - 64
     - public encryption key
     - uchar[]
     - The ECC public key used for encryption (uncompressed format;
       normally prepended with \x04 )
   * - 1+
     - nonce_trials_per_byte
     - var_int
     - Used to calculate the difficulty target of messages accepted by this
       node. The higher this value, the more difficult the Proof of Work must
       be before this individual will accept the message. This number is the
       average number of nonce trials a node will have to perform to meet the
       Proof of Work requirement. 1000 is the network minimum so any lower
       values will be automatically raised to 1000.
   * - 1+
     - extra_bytes
     - var_int
     - Used to calculate the difficulty target of messages accepted by this
       node. The higher this value, the more difficult the Proof of Work must
       be before this individual will accept the message. This number is added
       to the data length to make sending small messages more difficult.
       1000 is the network minimum so any lower values will be automatically
       raised to 1000.
   * - 1+
     - sig_length
     - var_int
     - Length of the signature
   * - sig_length
     - signature
     - uchar[]
     - The ECDSA signature which, as of protocol v3, covers the object
       header starting with the time, appended with the data described in this
       table down to the extra_bytes.

.. list-table:: A version 4 pubkey
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 32
     - tag
     - uchar[]
     - The tag, made up of bytes 32-64 of the double hash of the address data
       (see example python code below)
   * - ?
     - encrypted
     - uchar[]
     - Encrypted pubkey data.

When version 4 pubkeys are created, most of the data in the pubkey is encrypted.
This is done in such a way that only someone who has the Bitmessage address
which corresponds to a pubkey can decrypt and use that pubkey. This prevents
people from gathering pubkeys sent around the network and using the data from
them to create messages to be used in spam or in flooding attacks.

In order to encrypt the pubkey data, a double SHA-512 hash is calculated from
the address version number, stream number, and ripe hash of the Bitmessage
address that the pubkey corresponds to. The first 32 bytes of this hash are used
to create a public and private key pair with which to encrypt and decrypt the
pubkey data, using the same algorithm as message encryption
(see :doc:`encryption`). The remaining 32 bytes of this hash are added to the
unencrypted part of the pubkey and used as a tag, as above. This allows nodes to
determine which pubkey to decrypt when they wish to send a message.

In PyBitmessage, the double hash of the address data is calculated using the
python code below:

.. code-block:: python

    doubleHashOfAddressData = hashlib.sha512(hashlib.sha512(
        encodeVarint(addressVersionNumber) + encodeVarint(streamNumber) + hash
    ).digest()).digest()


.. list-table:: Encrypted data in version 4 pubkeys:
   :header-rows: 1
   :widths: auto

   * - Field Size
     - Description
     - Data type
     - Comments
   * - 4
     - behavior bitfield
     - uint32_t
     - A bitfield of optional behaviors and features that can be expected from
       the node receiving the message.
   * - 64
     - public signing key
     - uchar[]
     - The ECC public key used for signing (uncompressed format;
       normally prepended with \x04 )
   * - 64
     - public encryption key
     - uchar[]
     - The ECC public key used for encryption (uncompressed format;
       normally prepended with \x04 )
   * - 1+
     - nonce_trials_per_byte
     - var_int
     - Used to calculate the difficulty target of messages accepted by this
       node. The higher this value, the more difficult the Proof of Work must
       be before this individual will accept the message. This number is the
       average number of nonce trials a node will have to perform to meet the
       Proof of Work requirement. 1000 is the network minimum so any lower
       values will be automatically raised to 1000.
   * - 1+
     - extra_bytes
     - var_int
     - Used to calculate the difficulty target of messages accepted by this
       node. The higher this value, the more difficult the Proof of Work must
       be before this individual will accept the message. This number is added
       to the data length to make sending small messages more difficult.
       1000 is the network minimum so any lower values will be automatically
       raised to 1000.
   * - 1+
     - sig_length
     - var_int
     - Length of the signature
   * - sig_length
     - signature
     - uchar[]
     - The ECDSA signature which covers everything from the object header
       starting with the time, then appended with the decrypted data down to
       the extra_bytes. This was changed in protocol v3.

msg
^^^

Used for person-to-person messages. Note that msg objects won't contain a
version in the object header until Sun, 16 Nov 2014 22:00:00 GMT.

broadcast
^^^^^^^^^

Users who are subscribed to the sending address will see the message appear in
their inbox. Broadcasts are version 4 or 5.

Pubkey objects and v5 broadcast objects are encrypted the same way: The data
encoded in the sender's Bitmessage address is hashed twice. The first 32 bytes
of the resulting hash constitutes the "private" encryption key and the last
32 bytes constitute a tag so that anyone listening can easily decide if this
particular message is interesting. The sender calculates the public key from
the private key and then encrypts the object with this public key. Thus anyone
who knows the Bitmessage address of the sender of a broadcast or pubkey object
can decrypt it.

The version of broadcast objects was previously 2 or 3 but was changed to 4 or
5 for protocol v3. Having a broadcast version of 5 indicates that a tag is used
which, in turn, is used when the sender's address version is >=4.
