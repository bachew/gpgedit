# -*- coding: utf-8 -*-
import pytest
from gpgedit import GpgError, gpgedit


class edit(gpgedit):
    def run(self):
        super(edit, self).run()

        with open(self.plain_file) as f:
            self.plaintext = f.read()


@pytest.fixture
def cipher_file(tmpdir):
    cipher_file = tmpdir.join('cipher.gpg').strpath
    edit(cipher_file, write='plaintext\n', passphrase='passphrase')
    return cipher_file


def test_create_new(tmpdir):
    cipher_file = tmpdir.join('new.gpg')
    assert not cipher_file.check()
    edit(cipher_file.strpath, write='new plaintext', passphrase='passphrase')
    ciphertext = cipher_file.read()
    assert '-----BEGIN PGP MESSAGE-----' in ciphertext


def test_create_new_no_edit(tmpdir):
    cipher_file = tmpdir.join('new.gpg')
    assert not cipher_file.check()
    edit(cipher_file.strpath, passphrase='passphrase')
    ciphertext = cipher_file.read()
    assert '-----BEGIN PGP MESSAGE-----' in ciphertext


def test_decrypt(cipher_file):
    e = edit(cipher_file, passphrase='passphrase')
    assert e.plaintext == 'plaintext\n'


def test_decrypt_wrong_pass(cipher_file):
    with pytest.raises(GpgError):
        edit(cipher_file, passphrase='wrong passphrase')


def test_encrypt(cipher_file):
    edit(cipher_file, write='changes...\n', passphrase='passphrase')
    e = edit(cipher_file, passphrase='passphrase')
    assert e.plaintext == 'changes...\n'


def test_no_changes(cipher_file):
    edit(cipher_file, editor='cat', passphrase='passphrase')


# def test_change_passphrase(cipher_file):
#     edit(cipher_file,
#          decrypt_pass='passphrase', encrypt_pass='new passphrase',
#          change_pass=True)

#     with pytest.raises(GpgError):
#         edit(cipher_file, decrypt_pass='passphrase')

#     edit(cipher_file, decrypt_pass='new passphrase')
