Proof of work
=============

This page describes Bitmessage's Proof of work ("POW") mechanism as it exists in
Protocol Version 3. In this document, hash() means SHA512(). SHA512 was chosen
as it is widely supported and so that Bitcoin POW hardware cannot trivially be
used for Bitmessage POWs. The author acknowledges that they are essentially the
same algorithm with a different key size.

Both ``averageProofOfWorkNonceTrialsPerByte`` and ``payloadLengthExtraBytes``
are set by the owner of a Bitmessage address. The default and minimum for each
is 1000. (This is the same as difficulty 1. If the difficulty is 2, then this
value is 2000). The purpose of ``payloadLengthExtraBytes`` is to add some extra
weight to small messages.

Do a POW
--------

Let us use a ``msg`` message as an example::

   payload = embeddedTime + encodedObjectVersion + encodedStreamNumber + encrypted

``payloadLength``
   the length of payload, in bytes, + 8
   (to account for the nonce which we will append later)
``TTL``
   the number of seconds in between now and the object expiresTime.

.. include:: pow_formula.rst

::

   initialHash = hash(payload)

start with ``trialValue = 99999999999999999999``

also start with ``nonce = 0`` where nonce is 8 bytes in length and can be
hashed as if it is a string.

::

   while trialValue > target:
       nonce = nonce + 1
       resultHash = hash(hash( nonce || initialHash ))
       trialValue = the first 8 bytes of resultHash, converted to an integer

When this loop finishes, you will have your 8 byte nonce value which you can
prepend onto the front of the payload. The message is then ready to send.

Check a POW
-----------

Let us assume that ``payload`` contains the payload for a msg message (the nonce
down through the encrypted message data).

``nonce``
   the first 8 bytes of payload
``dataToCheck``
   the ninth byte of payload on down (thus it is everything except the nonce)

::

   initialHash = hash(dataToCheck)

   resultHash = hash(hash( nonce || initialHash ))

``POWValue``
   the first eight bytes of resultHash converted to an integer
``TTL``
   the number of seconds in between now and the object ``expiresTime``.

.. include:: pow_formula.rst

If ``POWValue`` is less than or equal to ``target``, then the POW check passes.



