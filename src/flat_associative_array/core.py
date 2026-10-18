"""Sorted associative array backed by two parallel lists.

Design notes
------------
The whole point of this structure is to avoid per-node object overhead.
A dict is almost always the right answer; this exists for the narrow case
where you have a few hundred keys, you need them in sorted order for range
scans or deterministic iteration, and you would rather not pay for a
hash table or a balanced-tree node per entry.

Keys are kept in a single sorted list, values in a parallel list at the
same index. Lookups use :func:`bisect.bisect_left`, which is CPython's
binary search over a list. Insertion into the middle of a list is O(n)
because of the memmove, so this structure is best when writes are rare
or when the dataset is small enough that the constant factor of two
flat lists beats the pointer-chasing of a tree.

Only totally-ordered keys are supported. We require keys to be mutually
comparable; mixing :class:`int` and :class:`str` raises ``TypeError``
from the comparison itself, which we let propagate rather than papering
over it with a silent fallback sort. Silent fallback sorts are how data
gets quietly misordered.
"""

from __future__ import annotations

import bisect
from typing import Iterator, Tuple


class FlatAssociativeArray:
    """A sorted associative array backed by two parallel lists.

    Keys are stored in sorted order in ``self._keys``; values are stored
    at the matching index in ``self._values``. Lookup is O(log n) via
    binary search; insertion and deletion are O(n) because of list
    shifting.
    """

    __slots__ = ("_keys", "_values")

    def __init__(self, items=None):
        """Initialize, optionally from an iterable of (key, value) pairs.

        If duplicate keys appear in *items*, later entries overwrite
        earlier ones, matching :class:`dict` construction semantics.
        """
        self._keys = []
        self._values = []
        if items is not None:
            for key, value in items:
                self._insert_or_replace(key, value)

    def _insert_or_replace(self, key, value) -> None:
        """Put *key* / *value* in, replacing an existing entry if present.

        Inline rather than delegating to :meth:`__setitem__` so the
        constructor does not pay for a redundant attribute lookup per
        item on large initial inputs.
        """
        idx = bisect.bisect_left(self._keys, key)
        if idx < len(self._keys) and self._keys[idx] == key:
            self._values[idx] = value
        else:
            self._keys.insert(idx, key)
            self._values.insert(idx, value)

    def __setitem__(self, key, value) -> None:
        """Set ``faa[key] = value``, inserting in sorted order or replacing."""
        self._insert_or_replace(key, value)

    def __getitem__(self, key):
        """Return the value for *key*, raising :class:`KeyError` if absent."""
        idx = bisect.bisect_left(self._keys, key)
        if idx < len(self._keys) and self._keys[idx] == key:
            return self._values[idx]
        raise KeyError(key)

    def __delitem__(self, key) -> None:
        """Delete *key*, raising :class:`KeyError` if absent."""
        idx = bisect.bisect_left(self._keys, key)
        if idx < len(self._keys) and self._keys[idx] == key:
            del self._keys[idx]
            del self._values[idx]
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        """Return the value for *key*, or *default* if absent.

        ``default`` is evaluated eagerly by the caller; we do not accept
        a zero-argument factory. That keeps the signature simple and
        avoids a hidden lambda allocation on every miss.
        """
        idx = bisect.bisect_left(self._keys, key)
        if idx < len(self._keys) and self._keys[idx] == key:
            return self._values[idx]
        return default

    def __contains__(self, key) -> bool:
        """Return ``True`` if *key* is present."""
        idx = bisect.bisect_left(self._keys, key)
        return idx < len(self._keys) and self._keys[idx] == key

    def __len__(self) -> int:
        """Return the number of entries."""
        return len(self._keys)

    def __iter__(self) -> Iterator:
        """Iterate over keys in sorted order."""
        return iter(self._keys)

    def keys(self):
        """Return a list view of the keys in sorted order.

        Returning a list (not a view) means mutations to the returned
        object do not affect the array, and mutations to the array do
        not retroactively change a previously-returned keys list. This
        is the least surprising behaviour for a small, pure-Python
        data structure.
        """
        return list(self._keys)

    def values(self):
        """Return a list view of the values in key-sorted order."""
        return list(self._values)

    def items(self):
        """Return a list of (key, value) pairs in key-sorted order."""
        return list(zip(self._keys, self._values))

    def __iter_keys__(self) -> Iterator:
        """Internal: used by range scan to avoid a list copy."""
        return iter(self._keys)

    def range(self, start=None, stop=None) -> Iterator[Tuple]:
        """Yield (key, value) pairs with ``start <= key < stop``.

        Either bound may be ``None`` to mean unbounded. Keys are yielded
        in sorted order. This is the main reason to prefer this structure
        over a plain :class:`dict`: you can slice the key space without
        materialising the whole key list.

        The half-open ``[start, stop)`` interval matches Python's slice
        semantics and :class:`range`. If you need ``[start, stop]``
        (inclusive), call ``range(start, None)`` and break out of the
        iterator yourself; we do not add a second parameter because two
        interval conventions in one method is exactly the kind of
        ambiguity that produces silent off-by-one bugs.
        """
        if start is None:
            lo = 0
        else:
            lo = bisect.bisect_left(self._keys, start)
        if stop is None:
            hi = len(self._keys)
        else:
            hi = bisect.bisect_left(self._keys, stop)
        for i in range(lo, hi):
            yield self._keys[i], self._values[i]

    def __eq__(self, other) -> bool:
        """Equal if *other* is a FlatAssociativeArray with same key/value pairs."""
        if isinstance(other, FlatAssociativeArray):
            return self._keys == other._keys and self._values == other._values
        return NotImplemented

    def __repr__(self) -> str:
        """Developer representation showing sorted contents."""
        body = ", ".join(f"{k!r}: {v!r}" for k, v in zip(self._keys, self._values))
        return f"FlatAssociativeArray({{{body}}})"
