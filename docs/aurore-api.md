
```
aurore [-h] [-C COLLECTION [COLLECTION ...]] [-F [ELEM:ATTRIB:]REGEX] [-R RECIPEFILE] [-v] [-q]
              {clone,git,post,copy,feed,rename} ...

rendre [-h] COLLECTION TEMPLATE [TEMPLATE-OPTIONS]
```

Global:
<!-- -C/--collection -->
-C/--config
<!-- -C/--cache-file -->
-I/--include (uri)
<!-- -I/--include -->
<!-- -E/--exclude -->
-B/--base-uri
<!-- -N/--namespace -->
-S/--setting-file
<!-- -R/--recipe -->
-F/--field-filter
<!-- -L/--local -->

-h/--help
-v/--verbose
-q/--quiet
-o/--output

Commands:
<!-- table -p/--print -x/--print-xpath -d/--delimiter[json,c,t] -->
<!-- feed -t/--template -p/--print -->
copy -c/--clean
get (fetch)  -n/--name
info  ITEM
list  --category
add
new 
put(edit)  -b/--batch-file  -f/--(write)field
post(new) -r/--readme -f/--field -s/--source-path -i/--init
show [<options>] [<object>...]
list []
print --map
describe


### `fetch`

Aggregates feed by calling `get` for every entry in collection.

>`aurore fetch | rendre templ-0003 >  gallery.html`

--template-data deprecated, instead specify as categories
> `aurore -F [[FIELD]:REGEX] feed`

### `copy`

>`aurore copy 

### `post` (new)

>`aurore post [-r README]` create directory entry from README file
>`aurore post -s SOURCEPATH -f t:Title -f d:DESCRIPTION` create single-file entry from source file

### `get`




### `put` (update)

>`aurore put -e ENTRY.atom`
>`aurore put -b FEED.atom`
>`aurore put qfem-0012 -f "t:New Title"`

