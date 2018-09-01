# GpgEdit

GpgEdit uses GnuPG to encrypt your secrets into a simple gpg file.


## Installation

You can install from PyPI:

```console
$ pip install gpgedit
```

Or from zip URL:

```console
pip install https://github.com/bachew/gpgedit/archive/master.zip
```

Or install from cloned repo:

```consle
git clone https://github.com/bachew/gpgedit.git
pip install gpgedit
```


## Usage

To create new encrypted gpg:

<pre>
$ gpgedit tmp/x
<b>Enter passphrase:</b>
<b>Confirm passphrase (1/2):</b>
<b>Confirm passphrase (2/2):</b>
<b>kwrite '/dev/shm/x.op36kgx8/x'</b>
...
<b>Encrypting '/dev/shm/x.op36kgx8/x' to 'tmp/x'
gpg --yes -a --cipher-algo AES256 -c --passphrase-file /dev/shm/x.op36kgx8/passphrase.7zlszwz2 -o tmp/x /dev/shm/x.op36kgx8/x</b>
Reading passphrase from file descriptor 3
<b>Saved 'tmp/x'</b>
</pre>

To edit:

<pre>
$ gpgedit tmp/x
<b>Enter passphrase:</b>
<b>Decrypting 'tmp/x' to '/dev/shm/x.d059kzze/x'</b>
gpg --yes --passphrase-file /dev/shm/x.d059kzze/passphrase.dsl_gwa6 -o /dev/shm/x.d059kzze/x tmp/x
Reading passphrase from file descriptor 3
gpg: AES256 encrypted data
gpg: encrypted with 1 passphrase
<b>kwrite '/dev/shm/x.d059kzze/x'</b>
...
<b>Encrypting '/dev/shm/x.d059kzze/x' to 'tmp/x'</b>
gpg --yes -a --cipher-algo AES256 -c --passphrase-file /dev/shm/x.d059kzze/passphrase.kbp9kerp -o tmp/x /dev/shm/x.d059kzze/x
Reading passphrase from file descriptor 3
<b>Saved 'tmp/x'</b>
kwrite(3077) KDirWatch::removeFile: doesn't know "/dev/shm/x.d059kzze/x"
Remove '/dev/shm/x.d059kzze'
</pre>

Notice the output is verbose and there's no way to turn it off so that you see how it works everytime. Please take a look at <a href="https://github.com/bachew/gpgedit/blob/master/src/gpgedit.py"><code>gpgedit.py</code></a> knowing that GpgEdit doesn't send your secrets somewhere else!


## Development

To setup development environment, clone the repo, run init.py and activate virtual environment:

```console
$ python3 init.py
$ pipenv shell
$ gpgedit -h
```

`tmp` is listed in `.gitignore`, create it for use in testing:

```console
$ mkdir tmp
```

Run `tox` to run unit tests on Python 2.7 and 3.

Lastly, some manual tests:

```console
# Create new gpg file
$ gpgedit tmp/x.gpg

# Create new gpg file without changes
$ gpgedit tmp/y.gpg

# Edit existing gpg file
$ gpgedit tmp/x.gpg

# Edit but without changes
$ gpgedit tmp/x.gpg
```


### Release

Before releasing, make sure `README.md` is up-to-date. If you updated it, please preview it before committing:

```console
$ markdown_py README.md -f tmp/README.html
```

Increase `setup.py::config['version']`, commit and merge to master branch. Travis will build and deploy to [PyPI](https://pypi.python.org).
