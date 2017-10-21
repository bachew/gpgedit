# -*- coding: utf-8 -*-
import pytest
from gpgedit import GpgError, gpgedit


class edit(gpgedit):
    def edit(self):
        super(edit, self).edit()

        with open(self.plain_file) as f:
            self.plaintext = f.read()


@pytest.fixture
def cipher_file(tmpdir):
    cipher_file = tmpdir.join('cipher.gpg').strpath
    edit(cipher_file, write='plaintext\n', encrypt_pass='passphrase')
    return cipher_file


def test_create_new(tmpdir):
    cipher_file = tmpdir.join('new.gpg')
    assert not cipher_file.check()
    edit(cipher_file.strpath, write='new plaintext', encrypt_pass='passphrase')
    ciphertext = cipher_file.read()
    assert '-----BEGIN PGP MESSAGE-----' in ciphertext


def test_create_new_no_edit(tmpdir):
    cipher_file = tmpdir.join('new.gpg')
    assert not cipher_file.check()
    edit(cipher_file.strpath, encrypt_pass='passphrase')
    ciphertext = cipher_file.read()
    assert '-----BEGIN PGP MESSAGE-----' in ciphertext


def test_decrypt(cipher_file):
    e = edit(cipher_file, decrypt_pass='passphrase')
    assert e.plaintext == 'plaintext\n'


def test_decrypt_wrong_pass(cipher_file):
    with pytest.raises(GpgError):
        edit(cipher_file, decrypt_pass='wrong passphrase')


def test_encrypt(cipher_file):
    edit(cipher_file, write='changes...\n', decrypt_pass='passphrase')
    e = edit(cipher_file, decrypt_pass='passphrase')
    assert e.plaintext == 'changes...\n'


def test_no_changes(cipher_file):
    edit(cipher_file, editor='cat', decrypt_pass='passphrase')


def test_change_passphrase(cipher_file):
    edit(cipher_file, write='change passphrase\n',
         decrypt_pass='passphrase', encrypt_pass='new passphrase',
         change_pass=True)

    with pytest.raises(GpgError):
        edit(cipher_file, decrypt_pass='passphrase')

    e = edit(cipher_file, decrypt_pass='new passphrase')
    assert e.plaintext == 'change passphrase\n'
