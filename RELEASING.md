
Releasing cdstarcat
===================

Clone clld/cdstarcat and switch to the master branch. Then:

- Do platform test via tox:
```shell script
tox -r
```

- Make sure flake8 passes::
```shell script
flake8 src/
```

- Change version to the new version number in
  - setup.cfg
  - src/cdstarcat/__init__.py

- Commit your change of the version number:
```shell script
git commit -a -m "release <VERSION>"
```

- Create a release tag:
```shell script
git tag -a v<VERSION> -m "<VERSION> release"
```

- Release to PyPI:
```shell script
rm dist/*
python -m build -n
twine upload dist/*
```

- Push to GitHub:
```shell script
git push origin
git push --tags origin
```

- Increment the version number and append `.dev0` to start the new development cycle:
  - setup.cfg
  - src/cdstarcat/__init__.py

- Commit/push the version change:
```shell script
git commit -a -m "bump version for development"
git push origin
```
