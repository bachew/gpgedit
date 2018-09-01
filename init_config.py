def check_python_version(version):
    if version[:2] != (2, 7) and version < (3, 4):
        raise ValueError('requires either 2.7 or >=3.4')
