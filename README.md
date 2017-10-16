# GpgEdit

GpgEdit uses GnuPG to encrypt your secrets into a simple gpg file.

To install:

    pip install gpgedit

If you are afraid that PyPI repository can be compromised, you can always clone directly and install:

    git clone https://github.com/bachew/gpgedit.git
    pip install ./gpgedit

To create new encrypted gpg:

<pre>
$ gpgedit tmp/x.gpg
<b>kwrite '/dev/shm/x.gpg.uotc9z7g/plain'</b>
Saving new 'tmp/x.gpg'
<b>Enter passphrase:</b>
<b>Confirm passphrase (1/2):</b>
<b>Confirm passphrase (2/2):</b>
gpg --yes -a --cipher-algo AES256 -o tmp/x.gpg -c --passphrase-file /dev/shm/x.gpg.uotc9z7g/encrypt.pass /dev/shm/x.gpg.uotc9z7g/plain
Reading passphrase from file descriptor 3
Remove '/dev/shm/x.gpg.uotc9z7g'
</pre>

To edit:

<pre>
$ gpgedit tmp/x.gpg
<b>Decrypting 'tmp/x.gpg' into '/dev/shm/x.gpg.lj98z4sn/plain'</b>
<b>Enter passphrase:</b>
gpg --yes -o /dev/shm/x.gpg.lj98z4sn/plain --passphrase-file /dev/shm/x.gpg.lj98z4sn/decrypt.pass tmp/x.gpg
Reading passphrase from file descriptor 3
gpg: AES256 encrypted data
gpg: encrypted with 1 passphrase
kwrite '/dev/shm/x.gpg.lj98z4sn/plain'
<b>Saving 'tmp/x.gpg'</b>
gpg --yes -a --cipher-algo AES256 -o tmp/x.gpg -c --passphrase-file /dev/shm/x.gpg.lj98z4sn/decrypt.pass /dev/shm/x.gpg.lj98z4sn/plain
Reading passphrase from file descriptor 3
Remove '/dev/shm/x.gpg.lj98z4sn'
</pre>

Notice the output is verbose and there's no way to turn it off so that you see how it works everytime. Please take a look at <a href="https://github.com/bachew/gpgedit/blob/master/src/gpgedit.py"><code>gpgedit.py</code></a> knowing that GpgEdit doesn't send your secrets somewhere else!


## Development

To setup development environment, clone the repo, run bootstrap and activate virtual environment:

    $ ./bootstrap
    $ source gpgedit-py3*/bin/activate
    $ gpgedit -h

To test on Python 2.7:

    $ cat > bootstrap_config_test.py
    python = 'python2'
    venv_dir = 'gpgedit-py2.7'
    $ ./bootstrap
    $ source gpgedit-py2.7/bin/activate
    $ gpgedit -h

`tmp` is listed in `.gitignore`, create it for use in testing:

    $ mkdir tmp

Run `tox` to run unit tests on Python 2.7 and 3.

Lastly, some manual tests:

    # Create new gpg file
    $ gpgedit tmp/x.gpg

    # Create new gpg file without changes
    $ gpgedit tmp/y.gpg

    # Edit existing gpg file
    $ gpgedit tmp/x.gpg

    # Edit but without changes
    $ gpgedit tmp/x.gpg


### Release

Before releasing, make sure `README.md` is up-to-date. If you updated it, please preview it before committing:

    $ markdown_py README.md -f tmp/README.html

Increase `setup.py::config['version']`, commit and merge to master branch. Travis will build and deploy to [PyPI](https://pypi.python.org).
