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
              help='Prompt for new passphrase to encrypt after editing')
@click.argument('gpg_file')
def cli(editor, echo, change_passphrase, gpg_file):
    try:
        if echo:
            editor = 'echo'

        gpgedit(gpg_file,
                change_pass=change_passphrase,
                editor=editor,
                ask_pass=True)
    except GpgError as e:
        echo_error(str(e))
        raise SystemExit(1)


cli.help = 'GpgEdit {} lets you edit a gpg-encrypted file.'.format(VERSION)


class gpgedit(object):
    CONFIRM_PASSPHRASE = 2
    AUTO_SAVE_INTERVAL = 0.5

    def __init__(self, cipher_file,
                 write=None, editor='echo',
                 passphrase=None,
                 change_pass=False, ask_pass=False,
                 **kwargs):

        self.cipher_file = cipher_file
        self.write = write
        self.editor = editor or self.detect_editor()
        self.passphrase = passphrase
        self.change_pass = change_pass
        self.ask_pass = ask_pass

        # Make opened files accessible only by current user
        orig_umask = os.umask(0o077)

        try:
            prefix = osp.basename(self.cipher_file) + '.'
            self.temp_dir = tempfile.mkdtemp(dir=SECURE_DIR, prefix=prefix)

            try:
                self.run(**kwargs)
            finally:
                echo('Remove {}'.format(srepr(self.temp_dir)))
                shutil.rmtree(self.temp_dir)
        finally:
            os.umask(orig_umask)

    def run(self):
        self.plain_file = osp.join(self.temp_dir, osp.basename(self.cipher_file))
        self.passphrase_file = None

        if osp.exists(self.cipher_file):
            echo_bold('Decrypting {} into {}'.format(srepr(self.cipher_file), srepr(self.plain_file)))
            self.get_passphrase_file()
            decrypt(self.cipher_file, self.plain_file, self.passphrase_file)

        # TODO: looks messy
        if not self.passphrase_file or self.change_pass:
            self.get_passphrase_file(confirm=self.CONFIRM_PASSPHRASE)

        self.editing = True
        self.last_modified = last_modified(self.plain_file)

        threads = [
            gevent.spawn(self.edit),
            gevent.spawn(self.auto_save),
        ]
        gevent.joinall(threads, raise_error=True)
        self.save()

    def edit(self):
        if self.write:
            echo_bold('Write {}'.format(srepr(self.plain_file)))

            with open(self.plain_file, 'w') as f:
                f.write(self.write)
                time.sleep(0.01)  # XXX: enough time to flush stat cache
        else:
            echo_bold('{} {}'.format(self.editor, srepr(self.plain_file)))
            click.edit(editor=self.editor, filename=self.plain_file)

        self.editing = False

    def auto_save(self):
        while self.editing:
            gevent.sleep(self.AUTO_SAVE_INTERVAL)
            self.save()

    def save(self):
        if osp.exists(self.cipher_file) and self.last_modified == last_modified(self.plain_file):
            return

        echo_bold('Saving {}'.format(srepr(self.cipher_file)))

        # Create if not exists
        if not osp.exists(self.plain_file):
            open(self.plain_file, 'w').close()

        encrypt(self.plain_file, self.cipher_file, self.passphrase_file)
        echo_bold('Saved {}'.format(srepr(self.cipher_file)))
        self.last_modified = last_modified(self.plain_file)

    def detect_editor(self):
        # Modified from click._termui_impl:Editor.get_editor()
        for key in 'VISUAL', 'EDITOR':
            editor = os.environ.get(key)

            if editor:
                return editor

        if sys.platform.startswith('win'):
            return 'notepad'

        for editor in 'gedit', 'kwrite', 'nano', 'vim':
            if os.system('which {} >/dev/null 2>&1'.format(editor)) == 0:
                return editor

        return 'vi'

    def get_passphrase_file(self, confirm=0):
        if self.passphrase_file:
            return

        if not self.passphrase:
            if not self.ask_pass:
                raise ValueError('No passphrase and ask_pass is False')

            self.passphrase = self.ask_passphrase(confirm)

        fd, path = tempfile.mkstemp(dir=self.temp_dir, prefix='passphrase.')
        os.write(fd, self.passphrase.encode(DEFAULT_ENCODING))
        os.close(fd)
        self.passphrase_file = path

    def ask_passphrase(self, confirm):
        def get(prompt):
            return getpass(click.style(prompt, bold=True))

        while True:
            p1 = get('Enter passphrase: ')

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


def decrypt(cipher_file, plain_file, pass_file=None):
    cmd = ['gpg', '--yes', '-o', plain_file]
    add_pass_option(cmd, pass_file)
    cmd.append(cipher_file)

    try:
        run(cmd)
    except subprocess.CalledProcessError:
        raise GpgError('Decryption failed!')


def encrypt(plain_file, cipher_file, pass_file=None):
    cmd = [
        'gpg', '--yes', '-a',
        '--cipher-algo', 'AES256',
        '-o', cipher_file, '-c'
    ]
    add_pass_option(cmd, pass_file)
    cmd.append(plain_file)

    try:
        run(cmd)
    except subprocess.CalledProcessError:
        raise GpgError('Encryption failed!')


def add_pass_option(cmd, pass_file):
    if not pass_file:
        raise ValueError('pass_file must be provided')

    cmd += ['--passphrase-file', pass_file]


def last_modified(filename):
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
