# GpgEdit

GpgEdit uses GnuPG to encrypt your secrets into a simple gpg file.

To install:

    pip install gpgedit

If you are afraid that PyPI repository can be compromised, you can always clone directly and install:

    git clone https://github.com/bachew/gpgedit.git
    pip install ./gpgedit

To create new encrypted gpg:

<pre>
$ gpgedit secrets.gpg
<em>Launch editor</em>
<strong>Saving new 'secrets.gpg', please enter a new passphrase</strong>
gpg --yes -a --cipher-algo AES256 -o secrets.gpg -c /dev/shm/secrets.gpg.itje9kbg
Enter passphrase: **********
Repeat passphrase: **********
Removing temporary file '/dev/shm/secrets.gpg.itje9kbg'
</pre>

To edit:

<pre>
$ gpgedit secrets.gpg
<strong>Decrypting 'secrets.gpg' into '/dev/shm/secrets.9jyn3bw5' for editing</strong>
gpg --yes -o /dev/shm/secrets.9jyn3bw5 secrets.gpg
gpg: AES256 encrypted data
Enter passphrase: **********
Repeat passphrase: **********
gpg: encrypted with 1 passphrase
<em>Launch editor</em>
<strong>Saving changes into 'secrets.gpg', you may enter a new passphrase</strong>
gpg --yes -a --cipher-algo AES256 -o secrets.gpg -c /dev/shm/secrets.gpg.9jyn3bw5
Enter passphrase: **********
Repeat passphrase: **********
Removing temporary file '/dev/shm/secrets.gpg.9jyn3bw5'
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

Since GpgEdit is very simple, just run these manual tests:

    # Create new gpg file
    $ gpgedit tmp/x.gpg

    # Create new gpg file without changes
    $ gpgedit tmp/y.gpg

    # Edit existing gpg file
    $ gpgedit tmp/x.gpg

    # Edit but without changes
    $ gpgedit tmp/x.gpg

Also run tox to make sure package and install work:

    tox


### Release

Before releasing, make sure `README.md` is up-to-date. If you updated it, please preview it before committing:

    $ markdown_py README.md -f tmp/README.html

Increase `setup.py::config['version']`, commit and merge to master branch. Travis will build and deploy to [Test PyPI](https://testpypi.python.org). You can then test installation:

    $ pip uninstall gpgedit
    $ gpgedit  # error: No such file or directory
    $ pip install -i https://testpypi.python.org/simple/ gpgedit
    $ gpgedit -h  # check version

After that [create a new release](https://github.com/bachew/gpgedit/releases) with the same version number but with `v` prefix. Travis will then build and deploy to [PyPI](https://pypi.python.org). You can then test installation as before but without specifying index URL:

    $ pip install gpgedit
