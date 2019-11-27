
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
  - setup.py
  - src/cdstarcat/__init__.py

- Commit your change of the version number:
```shell script
git commit -a -m "release <VERSION>"
```

- Create a release tag:
```shell script
git tag -a v<VERSION> -m "<VERSION> release"
```

- Release to PyPI (see https://github.com/di/markdown-description-example/issues/1#issuecomment-374474296):
```shell script
rm dist/*
python setup.py sdist
twine upload dist/*
rm dist/*
python setup.py bdist_wheel
twine upload dist/*
```

- Push to GitHub:
```shell script
git push origin
git push --tags origin
```

- Increment the version number and append `.dev0` to start the new development cycle:
  - setup.py
  - src/cdstarcat/__init__.py

- Commit/push the version change:
```shell script
git commit -a -m "bump version for development"
git push origin
```
