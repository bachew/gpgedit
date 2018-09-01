import os
from invoke import task
from os import path as osp
from subprocess import list2cmdline


repo_url = 'https://upload.pypi.org/legacy/'


os.chdir(osp.dirname(osp.dirname(__file__)))


@task
def init(ctx):
    pass  # nothing


@task
def test(ctx):
    ctx.run('tox')


@task
def build(ctx):
    ctx.run('rm -rf build dist')
    ctx.run('python setup.py sdist bdist_wheel')


@task
def upload(ctx):
    cmd = [
        'twine',
        'upload',
        '--repository-url', repo_url,
        '-u', 'bachew',
        'dist/*.whl'
    ]
    ctx.run(list2cmdline(cmd))


@task
def all(ctx):
    ctx.run('inv test build upload')
