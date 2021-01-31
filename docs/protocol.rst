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

Pubkey bitfield features
""""""""""""""""""""""""


.. _msg-types:

Message types
-------------

Undefined messages received on the wire must be ignored.

version
^^^^^^^

When a node creates an outgoing connection, it will immediately advertise its
version. The remote node will respond with its version. No futher communication
is possible until both peers have exchanged their version.


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

inv
^^^

Allows a node to advertise its knowledge of one or more objects. Payload
(maximum payload length: 50000 items):


getdata
^^^^^^^

getdata is used in response to an inv message to retrieve the content of a
specific object after filtering known elements.

Payload (maximum payload length: 50000 entries):


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


pubkey
^^^^^^

A version 2 pubkey. This is still in use and supported by current clients but
new v2 addresses are not generated by clients.


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
