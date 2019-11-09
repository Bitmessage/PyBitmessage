# -*- coding: utf-8 -*-
"""
src/plugins/proxyconfig_stem.py
===================================
"""
import os
import logging
import random  # noseq
import tempfile

import stem
import stem.control
import stem.process
import stem.version


class DebugLogger(object):
    """Safe logger wrapper for tor and plugin's logs"""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self._logger = logging.getLogger('default')
        self._levels = {
            'err': 40,
            'warn': 30,
            'notice': 20
        }

    def __call__(self, line):
        try:
            level, line = line.split('[', 1)[1].split(']')
        except IndexError:
            # Plugin's debug or unexpected log line from tor
            self._logger.debug(line)
        else:
            self._logger.log(self._levels.get(level, 10), '(tor) %s', line)


def connect_plugin(config):  # pylint: disable=too-many-branches
    """Run stem proxy configurator"""
    logwrite = DebugLogger()
    if config.safeGet('bitmessagesettings', 'sockshostname') not in (
            'localhost', '127.0.0.1', ''
    ):
        # remote proxy is choosen for outbound connections,
        # nothing to do here, but need to set socksproxytype to SOCKS5!
        logwrite(
            'sockshostname is set to remote address,'
            ' aborting stem proxy configuration')
        return

    datadir = tempfile.mkdtemp()
    control_socket = os.path.join(datadir, 'control')
    tor_config = {
        'SocksPort': '9050',
        # 'DataDirectory': datadir,  # had an exception with control socket
        'ControlSocket': control_socket
    }
    port = config.safeGet('bitmessagesettings', 'socksport', '9050')
    for attempt in range(50):
        if attempt > 0:
            port = random.randint(32767, 65535)
            tor_config['SocksPort'] = str(port)
        # It's recommended to use separate tor instance for hidden services.
        # So if there is a system wide tor, use it for outbound connections.
        try:
            stem.process.launch_tor_with_config(
                tor_config, take_ownership=True, timeout=20,
                init_msg_handler=logwrite)
        except OSError:
            if not attempt:
                try:
                    stem.version.get_system_tor_version()
                except IOError:
                    return
            continue
        else:
            logwrite('Started tor on port %s' % port)
            break

    if config.safeGetBoolean('bitmessagesettings', 'sockslisten'):
        # need a hidden service for inbound connections
        try:
            controller = stem.control.Controller.from_socket_file(
                control_socket)
            controller.authenticate()
        except stem.SocketError:
            # something goes wrong way
            logwrite('Failed to instantiate or authenticate on controller')
            return

        onionhostname = config.safeGet('bitmessagesettings', 'onionhostname')
        onionkey = config.safeGet(onionhostname, 'privsigningkey')
        if onionhostname and not onionkey:
            logwrite('The hidden service found in config ): %s' % onionhostname)
        onionkeytype = config.safeGet(onionhostname, 'keytype')

        response = controller.create_ephemeral_hidden_service(
            config.safeGetInt('bitmessagesettings', 'onionport', 8444),
            key_type=(onionkeytype or 'NEW'),
            key_content=(onionkey or onionhostname and 'ED25519-V3' or 'BEST')
        )

        if not response.is_ok():
            logwrite('Bad response from controller ):')
            return

        if not onionkey:
            logwrite('Started hidden service %s.onion' % response.service_id)
            # only save new service keys if onionhostname was not set previously
            if not onionhostname:
                onionhostname = response.service_id + '.onion'
                config.set(
                    'bitmessagesettings', 'onionhostname', onionhostname)
                config.add_section(onionhostname)
                config.set(
                    onionhostname, 'privsigningkey', response.private_key)
                config.set(
                    onionhostname, 'keytype', response.private_key_type)
                config.save()
        config.set('bitmessagesettings', 'socksproxytype', 'SOCKS5')

        return True
