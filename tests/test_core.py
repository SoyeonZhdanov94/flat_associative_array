import unittest

from flat_associative_array import FlatAssociativeArray


class TestConstruction(unittest.TestCase):
    def test_empty_by_default(self):
        faa = FlatAssociativeArray()
        self.assertEqual(len(faa), 0)
        self.assertEqual(faa.items(), [])

    def test_construct_from_pairs(self):
        faa = FlatAssociativeArray([(3, "c"), (1, "a"), (2, "b")])
        self.assertEqual(faa.items(), [(1, "a"), (2, "b"), (3, "c")])

    def test_construct_from_dict_preserves_sorted_order(self):
        faa = FlatAssociativeArray({2: "b", 1: "a"}.items())
        self.assertEqual(faa.keys(), [1, 2])

    def test_duplicate_keys_in_constructor_last_wins(self):
        faa = FlatAssociativeArray([(1, "first"), (1, "second")])
        self.assertEqual(faa[1], "second")
        self.assertEqual(len(faa), 1)


class TestGetSet(unittest.TestCase):
    def test_setitem_new_key_inserts_sorted(self):
        faa = FlatAssociativeArray()
        faa[2] = "b"
        faa[1] = "a"
        faa[3] = "c"
        self.assertEqual(faa.keys(), [1, 2, 3])
        self.assertEqual(faa.values(), ["a", "b", "c"])

    def test_setitem_existing_key_replaces_value(self):
        faa = FlatAssociativeArray([(1, "a")])
        faa[1] = "updated"
        self.assertEqual(faa[1], "updated")
        self.assertEqual(len(faa), 1)

    def test_getitem_missing_raises_keyerror(self):
        faa = FlatAssociativeArray([(1, "a")])
        with self.assertRaises(KeyError):
            _ = faa[99]

    def test_getitem_present_returns_value(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        self.assertEqual(faa[2], "b")

    def test_get_missing_returns_default(self):
        faa = FlatAssociativeArray([(1, "a")])
        self.assertEqual(faa.get(1), "a")
        self.assertEqual(faa.get(99), None)
        self.assertEqual(faa.get(99, "fallback"), "fallback")

    def test_contains(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        self.assertIn(1, faa)
        self.assertIn(2, faa)
        self.assertNotIn(3, faa)


class TestDelete(unittest.TestCase):
    def test_delitem_existing(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b"), (3, "c")])
        del faa[2]
        self.assertEqual(faa.keys(), [1, 3])
        self.assertEqual(faa.values(), ["a", "c"])

    def test_delitem_first(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        del faa[1]
        self.assertEqual(faa.keys(), [2])

    def test_delitem_last(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        del faa[2]
        self.assertEqual(faa.keys(), [1])

    def test_delitem_missing_raises_keyerror(self):
        faa = FlatAssociativeArray([(1, "a")])
        with self.assertRaises(KeyError):
            del faa[99]

    def test_delitem_from_empty_raises_keyerror(self):
        faa = FlatAssociativeArray()
        with self.assertRaises(KeyError):
            del faa[1]


class TestIteration(unittest.TestCase):
    def test_iter_yields_keys_sorted(self):
        faa = FlatAssociativeArray([(3, "c"), (1, "a"), (2, "b")])
        self.assertEqual(list(iter(faa)), [1, 2, 3])

    def test_items_sorted(self):
        faa = FlatAssociativeArray([(3, "c"), (1, "a"), (2, "b")])
        self.assertEqual(faa.items(), [(1, "a"), (2, "b"), (3, "c")])

    def test_keys_returns_list_copy(self):
        faa = FlatAssociativeArray([(1, "a")])
        k = faa.keys()
        k.append(99)
        self.assertEqual(faa.keys(), [1])

    def test_values_returns_list_copy(self):
        faa = FlatAssociativeArray([(1, "a")])
        v = faa.values()
        v.append("x")
        self.assertEqual(faa.values(), ["a"])


class TestRange(unittest.TestCase):
    def test_range_full(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b"), (3, "c"), (4, "d")])
        self.assertEqual(list(faa.range()), faa.items())

    def test_range_with_start_only(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b"), (3, "c"), (4, "d")])
        self.assertEqual(list(faa.range(3)), [(3, "c"), (4, "d")])

    def test_range_with_stop_only(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b"), (3, "c"), (4, "d")])
        self.assertEqual(list(faa.range(None, 3)), [(1, "a"), (2, "b")])

    def test_range_half_open(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b"), (3, "c"), (4, "d")])
        self.assertEqual(list(faa.range(2, 4)), [(2, "b"), (3, "c")])

    def test_range_empty_when_no_keys_in_bounds(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        self.assertEqual(list(faa.range(10, 20)), [])

    def test_range_start_equals_stop_yields_empty(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        self.assertEqual(list(faa.range(1, 1)), [])

    def test_range_on_empty_array(self):
        faa = FlatAssociativeArray()
        self.assertEqual(list(faa.range(1, 10)), [])


class TestEqualityAndRepr(unittest.TestCase):
    def test_equal_arrays(self):
        a = FlatAssociativeArray([(1, "a"), (2, "b")])
        b = FlatAssociativeArray([(2, "b"), (1, "a")])
        self.assertEqual(a, b)

    def test_unequal_values(self):
        a = FlatAssociativeArray([(1, "a")])
        b = FlatAssociativeArray([(1, "b")])
        self.assertNotEqual(a, b)

    def test_unequal_keys(self):
        a = FlatAssociativeArray([(1, "a")])
        b = FlatAssociativeArray([(2, "a")])
        self.assertNotEqual(a, b)

    def test_eq_with_non_faa(self):
        a = FlatAssociativeArray([(1, "a")])
        self.assertNotEqual(a, [(1, "a")])

    def test_repr_roundtrip_friendly(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        r = repr(faa)
        self.assertIn("FlatAssociativeArray", r)
        self.assertIn("1: 'a'", r)
        self.assertIn("2: 'b'", r)


class TestEdgeCases(unittest.TestCase):
    def test_string_keys(self):
        faa = FlatAssociativeArray([("banana", 1), ("apple", 2), ("cherry", 3)])
        self.assertEqual(faa.keys(), ["apple", "banana", "cherry"])

    def test_negative_keys(self):
        faa = FlatAssociativeArray([(5, "e"), (-3, "c"), (0, "z")])
        self.assertEqual(faa.keys(), [-3, 0, 5])

    def test_overwrite_value_in_place(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b"), (3, "c")])
        faa[2] = "B"
        self.assertEqual(faa.values(), ["a", "B", "c"])
        self.assertEqual(len(faa), 3)

    def test_float_keys_comparable(self):
        faa = FlatAssociativeArray([(1.5, "a"), (0.5, "b")])
        self.assertEqual(faa.keys(), [0.5, 1.5])

    def test_clear_by_deleting_all(self):
        faa = FlatAssociativeArray([(1, "a"), (2, "b")])
        del faa[1]
        del faa[2]
        self.assertEqual(len(faa), 0)
        self.assertEqual(faa.items(), [])


if __name__ == "__main__":
    unittest.main()
