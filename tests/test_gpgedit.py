# -*- coding: utf-8 -*-
import pytest
from gpgedit import GpgError, gpgedit


@pytest.fixture
def cipher_file(tmpdir):
    cipher_file = tmpdir.join('cipher.gpg').strpath
    gpgedit(cipher_file, write='plaintext\n', encrypt_pass='passphrase')
    return cipher_file


def test_create_new(tmpdir):
    cipher_file = tmpdir.join('new.gpg')
    assert not cipher_file.check()
    gpgedit(cipher_file.strpath, write='new plaintext', encrypt_pass='passphrase')
    ciphertext = cipher_file.read()
    assert '-----BEGIN PGP MESSAGE-----' in ciphertext


def test_create_new_no_edit(tmpdir):
    cipher_file = tmpdir.join('new.gpg')
    assert not cipher_file.check()
    gpgedit(cipher_file.strpath, encrypt_pass='passphrase')
    ciphertext = cipher_file.read()
    assert '-----BEGIN PGP MESSAGE-----' in ciphertext


def test_decrypt(cipher_file):
    edit = gpgedit(cipher_file, decrypt_pass='passphrase', set_plaintext=True)
    assert edit.plaintext == 'plaintext\n'


def test_decrypt_wrong_pass(cipher_file):
    with pytest.raises(GpgError):
        gpgedit(cipher_file, decrypt_pass='wrong passphrase')


def test_encrypt(cipher_file):
    gpgedit(cipher_file, write='changes...\n', decrypt_pass='passphrase')
    edit = gpgedit(cipher_file, decrypt_pass='passphrase', set_plaintext=True)
    assert edit.plaintext == 'changes...\n'


def test_no_changes(cipher_file):
    gpgedit(cipher_file, editor='cat', decrypt_pass='passphrase')


def test_change_passphrase(cipher_file):
    gpgedit(cipher_file, write='change passphrase\n',
            decrypt_pass='passphrase', encrypt_pass='new passphrase',
            change_pass=True)

    with pytest.raises(GpgError):
        gpgedit(cipher_file, decrypt_pass='passphrase')

    edit = gpgedit(cipher_file, decrypt_pass='new passphrase', set_plaintext=True)
    assert edit.plaintext == 'change passphrase\n'
