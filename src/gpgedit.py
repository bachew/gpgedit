# -*- coding: utf-8 -*-
import gevent.monkey

gevent.monkey.patch_all()  # noqa

import click
import errno
import os
import gevent
import pkg_resources
import shutil
import sys
import subprocess
import tempfile
import time
from click import echo
from getpass import getpass
from os import path as osp


VERSION = pkg_resources.get_distribution('gpgedit').version
CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}
SECURE_DIR = '/dev/shm'
PY2 = sys.version_info[0] == 2
DEFAULT_ENCODING = 'utf-8'
OUTPUT_ENCODING = sys.stdout.encoding or DEFAULT_ENCODING


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-e', '--editor',
              help='Text editor, default auto-detect')
@click.option('-E', '--echo', is_flag=True,
              help="Equivalent to '-e echo'")
@click.option('--change-passphrase', is_flag=True,
              help='Re-encrypt with new phassphrase without editing')
@click.argument('gpg_file')
def cli(editor, echo, change_passphrase, gpg_file):
    try:
        if echo:
            editor = 'echo'

        gpgedit(gpg_file,
                change_passphrase=change_passphrase,
                editor=editor)
    except GpgError as e:
        echo_error(str(e))
        raise SystemExit(1)


cli.help = 'GpgEdit (v{}) lets you edit a gpg-encrypted file.'.format(VERSION)


class gpgedit(object):
    CONFIRM_PASSPHRASE = 2
    AUTOSAVE_INTERVAL = 0.5

    def __init__(self, cipher_file,
                 write=None, editor='echo',
                 passphrase=None, interactive=True,
                 change_passphrase=False, new_passphrase=None):

        self.cipher_file = cipher_file
        self.write = write
        self.editor = editor or self.detect_editor()
        self.passphrase = passphrase
        self.change_passphrase = change_passphrase
        self.new_passphrase = new_passphrase
        self.interactive = interactive

        # Make opened files accessible only by current user
        orig_umask = os.umask(0o077)

        try:
            prefix = osp.basename(self.cipher_file) + '.'
            self.temp_dir = tempfile.mkdtemp(dir=SECURE_DIR, prefix=prefix)

            try:
                self.run()
            finally:
                echo('Remove {}'.format(srepr(self.temp_dir)))
                shutil.rmtree(self.temp_dir)
        finally:
            os.umask(orig_umask)

    def run(self):
        self.plain_file = osp.join(self.temp_dir, osp.basename(self.cipher_file))

        if osp.exists(self.cipher_file):
            passphrase_ok = False

            while not passphrase_ok:
                try:
                    passphrase_file = self.get_passphrase_file()
                    echo_bold('Decrypting {} to {}'.format(srepr(self.cipher_file), srepr(self.plain_file)))
                    decrypt(self.cipher_file, self.plain_file, passphrase_file)
                except GpgError:
                    if not self.interactive:
                        raise

                    self.passphrase = None
                    echo_error('Decryption failed, please try again')
                else:
                    passphrase_ok = True
        else:
            echo('New file {!r} will be created'.format(self.cipher_file))
            self.get_passphrase_file(confirm=2)

        self.last_modified = mtime(self.plain_file)

        if not self.change_passphrase:
            self.editing = True
            threads = [
                gevent.spawn(self.edit),
                gevent.spawn(self.autosave),
            ]
            gevent.joinall(threads, raise_error=True)

        self.save()

    def edit(self):
        if self.write:
            echo_bold('Writing {}'.format(srepr(self.plain_file)))

            with open(self.plain_file, 'w') as f:
                f.write(self.write)
                time.sleep(0.01)  # XXX: allow enough time to flush stat cache
        else:
            echo_bold('{} {}'.format(self.editor, srepr(self.plain_file)))
            click.edit(editor=self.editor, filename=self.plain_file)

        self.editing = False

    def autosave(self):
        while self.editing:
            gevent.sleep(self.AUTOSAVE_INTERVAL)
            self.save()

    def save(self):
        if self.change_passphrase or not osp.exists(self.cipher_file) or self.last_modified != mtime(self.plain_file):

            # Create if not exists
            if not osp.exists(self.plain_file):
                open(self.plain_file, 'w').close()

            if self.change_passphrase:
                passphrase_file = self.get_passphrase_file(passphrase_attr='new_passphrase',
                                                           prompt='Enter new passphrase: ', confirm=2)
            else:
                passphrase_file = self.get_passphrase_file()

            echo_bold('Encrypting {} to {}'.format(srepr(self.plain_file), srepr(self.cipher_file)))
            encrypt(self.plain_file, self.cipher_file, passphrase_file)
            echo_bold('Saved {}'.format(srepr(self.cipher_file)))
            self.last_modified = mtime(self.plain_file)

    def detect_editor(self):
        for key in 'VISUAL', 'EDITOR':
            editor = os.environ.get(key)

            if editor:
                return editor

        for editor in 'gedit', 'kwrite', 'nano', 'vim':
            if os.system('which {} >/dev/null 2>&1'.format(editor)) == 0:
                return editor

        return 'vi'

    def get_passphrase_file(self, passphrase_attr='passphrase',
                            prompt='Enter passphrase: ', confirm=0):
        passphrase = getattr(self, passphrase_attr)

        if not passphrase:
            if not self.interactive:
                raise ValueError('No passphrase but interactive off')

            passphrase = self.ask_passphrase(prompt, confirm)
            setattr(self, passphrase_attr, passphrase)

        fd, path = tempfile.mkstemp(dir=self.temp_dir, prefix='passphrase.')
        os.write(fd, passphrase.encode(DEFAULT_ENCODING))
        os.close(fd)
        return path

    def ask_passphrase(self, prompt, confirm):
        def get(prompt):
            return getpass(click.style(prompt, bold=True))

        while True:
            p1 = get(prompt)

            if confirm <= 0:
                return p1

            all_match = True

            for i in range(confirm):
                p2 = get('Confirm passphrase ({}/{}): '.format(i + 1, confirm))

                if p1 != p2:
                    echo_error('Passphrase not match!')
                    all_match = False
                    break

            if all_match:
                return p1


class GpgError(Exception):
    pass


def echo_bold(message):
    click.secho(message, bold=True, err=True)


def echo_error(message):
    return echo(click.style(message, bold=True, fg='red'), err=True)


def run(cmdlist):
    cmdline = subprocess.list2cmdline(cmdlist)
    echo(cmdline)

    try:
        subprocess.check_call(cmdlist)
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise OSError('Command {} not found, did you install it?'.format(srepr(cmdlist[0])))

        raise


def decrypt(cipher_file, plain_file, passphrase_file):
    cmd = [
        'gpg', '--batch', '--yes',
        '--passphrase-file', passphrase_file,
        '-o', plain_file
    ]
    cmd.append(cipher_file)

    try:
        run(cmd)
    except subprocess.CalledProcessError:
        raise GpgError('Decryption failed!')


def encrypt(plain_file, cipher_file, passphrase_file):
    cmd = [
        'gpg', '--batch', '--yes', '-a',
        '--cipher-algo', 'AES256',
        '-c',
        '--passphrase-file', passphrase_file,
        '-o', cipher_file
    ]
    cmd.append(plain_file)

    try:
        run(cmd)
    except subprocess.CalledProcessError:
        raise GpgError('Encryption failed!')


def mtime(filename):
    try:
        return os.stat(filename).st_mtime
    except OSError as e:
        if e.errno == errno.ENOENT:
            return 0

        raise


def srepr(obj):
    '''
    String representation without 'u' prefix.
    '''
    if PY2 and isinstance(obj, unicode):
        obj = obj.encode(OUTPUT_ENCODING)

    return repr(obj)
