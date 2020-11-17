

```shell
# copy resources listed in Gallery.yaml to current dir,
# applying filters in aurore.filter.yaml
aurore update fdlb-xxxx.yaml meta.yaml
aurore update qfem-xxxx.yaml test-status.yaml meta.yaml
aurore update test-status.yaml status.yaml
```

```shell
# copy resources listed in qfem-xxxx.yaml to current dir,
# applying filters in aurore.filter.yaml
aurore copy qfem-xxxx.yaml . --filter aurore.filter.yaml --clean
```

### Report

```shell
$ aurore -q report qfem-xxxx.yaml status.yaml --title="quoFEM"> README.md
```

### Show

```shell
$SIMCENTER_DEV/quoFEM/examples$ aurore -q show qfem-xxxx.yaml 'q'
```