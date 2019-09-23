# -*- coding: utf-8 -*-
'''
Management of Podman Containers

:depends: Podman

.. note::
    This is a quick and dirty solution for management of Podman containers.

    Podman support is not yet available from SaltStack:
        https://github.com/saltstack/salt/issues/50624

    Likewise, the Python bindings for Podman are not yet packaged for SLE15:
        https://github.com/containers/python-podman

    This solution should be replaced when the above upstream components
    become available downstream.
'''

__docformat__ = 'restructuredtext en'

import functools
import logging
import salt.utils.path

from salt.exceptions import CommandExecutionError

PODMAN = 'podman'
PODMAN_BIN = salt.utils.path.which(PODMAN)
PODMAN_BIN_ERR = f'Could not find the \'{PODMAN}\' binary, is \'{PODMAN}\' installed?'

# Set up logging
log = logging.getLogger(__name__)

# Define the module's virtual name and alias
__virtualname__ = 'podman'
__virtual_aliases__ = ('podman-ng')


def __virtual__():
    '''
    Only load if the podman binary is present
    '''
    # TODO: remove? this produces a cryptic 'podman.run is not available' msg
    #if not PODMAN_BIN:
    #    return (False, PODMAN_BIN_ERR)
    return __virtualname__


def _validate(wrapped):
    '''
    Decorator for common function argument validation
    '''
    @functools.wraps(wrapped)
    def wrapper(*args, **kwargs):
        # TODO: add any validation here
        return wrapped(*args, **salt.utils.args.clean_kwargs(**kwargs))
    return wrapper


@_validate
def _cmd(command, command_args=[], **kwargs):
    '''
    TODO: docstring
    '''

    global_options = kwargs.get('global_options')
    cmd_func = kwargs.get('cmd_func', 'cmd.run_all')
    dry_run = kwargs.get('dry_run', False)

    if not PODMAN_BIN:
        raise CommandExecutionError(PODMAN_BIN_ERR)

    #
    # podman [global options] command [command options] [arguments...]
    #
    cmd = [ PODMAN_BIN ]
    if global_options:
        cmd += global_options
    cmd.append(command)
    if command_args:
        cmd += command_args

    if dry_run:
        ret = {}
    else:
        ret = __salt__[cmd_func](cmd, **kwargs)

    # TODO: create a wrapper or other func for this?
    # Augment the retval with additional context
    ret['cmd'] = cmd
    ret['kwargs'] = kwargs
    ret['cmd_func'] = cmd_func

    return ret


def _get_volumes_option(**kwargs):
    '''
    TODO: docstring
    '''
    ret = []
    volumes = kwargs.get('volumes')
    if volumes:
        for volume in volumes:
            ret += ['-v', volume]
    return ret


def run(image, options=[], command='', command_args=[], **kwargs):
    '''
    Equivalent to ``podman run`` on the Podman CLI. Runs the container, waits
    for it to exit, and returns the container's logs when complete.

    :param str image: The container image to run. ex: 'busybox'

    :param list options: The options to pass to the podman binary

    :param str command: The command to run within the container image

    :param list command_args: The arguments to pass to the command run within
        the container image

    CLI Examples:

    .. code-block:: bash

        # salt 'admin*' podman.run busybox command='echo' command_args='["hello from busybox"]'
    '''
    if not PODMAN_BIN:
        raise CommandExecutionError(PODMAN_BIN_ERR)

    options += _get_volumes_option(**kwargs)

    #
    # podman run [options] image [command [arg ...]]
    #
    run_args = []
    if options:
        run_args += options
    run_args.append(image)
    if command:
        run_args.append(command)
    if command_args:
        run_args += command_args

    return _cmd('run', run_args, **kwargs)

