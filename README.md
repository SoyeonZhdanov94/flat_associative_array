# flat_associative_array

A sorted associative array backed by two parallel Python lists, using `bisect` for O(log n) lookups. It keeps keys in sorted order at all times, which makes ordered iteration and range scans free.

## Usage

```python
from flat_associative_array import FlatAssociativeArray

faa = FlatAssociativeArray([(3, "c"), (1, "a"), (2, "b")])
faa[4] = "d"
print(faa[2])            # "b"
print(faa.keys())        # [1, 2, 3, 4]
print(list(faa.range(2, 4)))  # [(2, 'b'), (3, 'c')]
del faa[1]
print(len(faa))          # 3
```

## Why this exists

A plain `dict` is almost always the right data structure. This one exists for the narrow case where you need keys in sorted order — for range scans, deterministic iteration, or stable serialisation — and the dataset is small enough (a few hundred to a few thousand entries) that the per-node overhead of a balanced tree or the hash-table bookkeeping of a `dict` is not worth it. You get two flat lists, binary search on reads, and ordered iteration for free.

The trade-off: insertion and deletion are O(n) because inserting into the middle of a Python list shifts memory. Reads are O(log n). If your workload is write-heavy on a large dataset, use `sortedcontainers` or a tree; this library is intentionally minimal and depends on nothing outside the standard library.

## Exported API

- `FlatAssociativeArray(items=None)` — constructor; `items` is an optional iterable of `(key, value)` pairs. Duplicate keys in `items`: later entries overwrite earlier ones, matching `dict` semantics.
- `faa[key] = value` — insert or replace.
- `faa[key]` — get, raises `KeyError` if absent.
- `del faa[key]` — delete, raises `KeyError` if absent.
- `faa.get(key, default=None)` — get with fallback.
- `key in faa` — membership test.
- `len(faa)` — number of entries.
- `iter(faa)` — iterate keys in sorted order.
- `faa.keys()`, `faa.values()`, `faa.items()` — list views in sorted order.
- `faa.range(start=None, stop=None)` — iterator over `(key, value)` pairs with `start <= key < stop` (half-open, matching Python slice semantics). Either bound may be `None` for unbounded.
- `faa == other` — equality by contents.
- `repr(faa)` — developer representation.

## Edge cases

Keys must be mutually comparable; mixing incomparable types (e.g. `int` and `str`) raises `TypeError` from the comparison, which propagates rather than being silenced. `None` is usable as a key. `range()` is half-open `[start, stop)`, not inclusive — if you need inclusive bounds, iterate from `start` and break manually.
