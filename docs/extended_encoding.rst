Extended encoding
=================

Extended encoding is an attempt to create a standard for transmitting structured
data. The goals are flexibility, wide platform support and extensibility. It is
currently available in the v0.6 branch and can be enabled by holding "Shift"
while clicking on Send. It is planned that v5 addresses will have to support
this. It's a work in progress, the basic plain text message works but don't
expect anthing else at this time.

The data structure is in msgpack, then compressed with zlib. The top level is
a key/value store, and the "" key (empty string) contains the value of the type
of object, which can then have its individual format and standards.

Text fields are encoded using UTF-8.

Types
-----

You can find the implementations in the ``src/messagetypes`` directory of
PyBitmessage. Each type has its own file which includes one class, and they are
dynamically loaded on startup. It's planned that this will also contain
initialisation, rendering and so on, so that developers can simply add a new
object type by adding a single file in the messagetypes directory and not have
to change any other part of the code.

message
^^^^^^^

The replacement for the old messages. Mandatory keys are ``body`` and
``subject``, others are currently not implemented and not mandatory. Proposed
other keys:

``parents``:
   array of msgids referring to messages that logically precede it in a
   conversation. Allows to create a threaded conversation view

``files``:
   array of files (which is a key/value pair):

   ``name``:
      file name, mandatory
   ``data``:
      the binary data of the file
   ``type``:
      MIME content type
   ``disposition``:
      MIME content disposition, possible values are "inline" and "attachment"

vote
^^^^

Dummy code available in the repository. Supposed to serve voting in a chan
(thumbs up/down) for decentralised moderation. Does not actually do anything at
the moment and specification can change.
