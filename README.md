---
title: Aurore
summary: A distributed document-oriented database management system.
...

<h1>Aurore</h1>

A distributed document-oriented database management system.

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

