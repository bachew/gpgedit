# -*- coding: utf-8 -*-
import click
import errno
import os
import pkg_resources
import subprocess
import tempfile
from click import ClickException, echo
from os import path as osp


__version__ = pkg_resources.get_distribution('gpgedit').version

SECURE_DIR = '/dev/shm'
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('filename')
def main(filename):
    '''
    Edit a gpg-encrypted file.
    '''
    _, edit_file = tempfile.mkstemp(prefix=osp.basename(filename) + '.', dir=SECURE_DIR)

    try:
        if osp.exists(filename):
            echo_bold('Decrypting {!r} into {!r} for editing'.format(filename, edit_file))
            decrypt(filename, edit_file)

        updated = edit(edit_file)
        save = True

        if osp.exists(filename):
            if updated:
                echo_bold('Saving changes into {!r}, you may enter a new passphrase'.format(filename))
            else:
                echo_bold('No changes')
                save = False
        else:
            echo_bold('Saving new {!r}, please enter a new passphrase'.format(filename))

        if save:
            encrypt(edit_file, filename)
    finally:
        echo('Removing temporary file {!r}'.format(edit_file))
        remove(edit_file)


main.help = 'GpgEdit v{}, lets you edit a gpg-encrypted file.'.format(__version__)


def echo_bold(message):
    click.secho(message, bold=True)


def run(cmdlist):
    cmdline = subprocess.list2cmdline(cmdlist)
    echo(cmdline)

    try:
        subprocess.check_call(cmdlist)
    except subprocess.CalledProcessError:
        raise ClickException(cmdline)  # suppress stack trace, command output's enough
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise ClickException('Command {!r} not found, did you install it?'.format(cmdlist[0]))

        raise


def encrypt(plain_file, cipher_file):
    run(['gpg', '--yes', '-a',
         '--cipher-algo', 'AES256',
         '-o', cipher_file, '-c', plain_file])


def decrypt(cipher_file, plain_file):
    run(['gpg', '--yes', '-o', plain_file, cipher_file])


def edit(filename):
    t = mtime(filename)
    click.edit(filename=filename)
    return t != mtime(filename)


def remove(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise


def mtime(filename):
    try:
        return os.stat(filename).st_mtime
    except OSError as e:
        if e.errno == errno.ENOENT:
            return 0

        raise
