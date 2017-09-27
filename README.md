# GpgEdit

GpgEdit uses GnuPG to encrypt your secrets into a simple gpg file.

To install:

    pip install gpgedit

To create new encrypted gpg:

    $ gpgedit secrets.gpg
    Saving new 'secrets.gpg', please enter a new passphrase
    gpg --yes -a --cipher-algo AES256 -o secrets.gpg -c /dev/shm/secrets.itje9kbg
    Enter passphrase: **********
    Repeat passphrase: **********
    Removing temporary file '/dev/shm/secrets.itje9kbg'

To edit:

    $ gpgedit secrets.gpg
    Decrypting 'secrets.gpg' into '/dev/shm/secrets.9jyn3bw5' for editing
    gpg --yes -o /dev/shm/secrets.9jyn3bw5 secrets.gpg
    gpg: AES256 encrypted data
    gpg: encrypted with 1 passphrase
    Saving changes into 'secrets.gpg', you may enter a new passphrase
    gpg --yes -a --cipher-algo AES256 -o secrets.gpg -c /dev/shm/secrets.9jyn3bw5
    Enter passphrase: **********
    Repeat passphrase: **********
    Removing temporary file '/dev/shm/secrets.9jyn3bw5'
