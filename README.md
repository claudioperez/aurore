---
title: Aurore
summary: A distributed document-oriented database management system.
...

<h1>Aurore</h1>

A distributed document-oriented database management system.

---------------------------

[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Commits since latest release][gh-image]][gh-link]

## Synopsis

```shell
aurore [-h] [-D [DATABASE_FILE]] [-B BASE_URI] [-d [DEFAULTS]] [-v]
       [-q] [--version]
       {post,get} ...
```

## Options

<dl>
  <dt>-v, --verbose</dt>
  <dd>Generate verbose output.</dd>
  <dt>-q, --quiet</dt>
  <dd>Suppress logging output.</dd>
  <dt>-h, --help</dt>
  <dd>Print a brief help message.</dd>
</dl>



## Configuration

### Global (`~/.local/shared/aurore/global.yaml`)

```
env_vars: {}
def-defaults: !defaults {}
```

### Local (`.aurore/config.yaml`)

```yaml
types: <types>
def-defaults: <defaults>
```

[pypi-v-image]: https://img.shields.io/pypi/v/aurore.svg
[pypi-v-link]: https://pypi.org/project/aurore/

[gh-link]: https://github.com/claudioperez/aurore/compare/0.0.1...master
[gh-image]: https://img.shields.io/github/commits-since/claudioperez/aurore/0.0.1?style=social
