from collections import defaultdict


def split_first_arg(func):
    def wrapper(self, arg, *args, **kwargs):
        if isinstance(arg, str):
            arg_parts = arg.split(self.delim)
            return func(self, arg_parts, *args, **kwargs)
        assert isinstance(arg, list)  # already split...
        return func(self, arg, *args, **kwargs)

    return wrapper


def split_kwarg(kwarg):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if kwarg in kwargs and isinstance(kwargs[kwarg], str):
                kwargs[kwarg] = kwargs[kwarg].split(self.delim)
                return func(self, *args, **kwargs)
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class EventDict:
    delim = "::"
    wildcard = "*"

    def __init__(self):
        self._children = dict()  # more nested dicts
        self._data = set()

    @split_first_arg
    def add(self, key, value):
        if len(key) == 0:
            return self._data.add(value)
        if not key[0] in self._children:
            self._children[key[0]] = EventDict()
        self._children[key[0]].add(key[1:], value)

    @split_first_arg
    def remove(self, key, value):
        if len(key) == 0:
            self._data.discard(value)
            for v in self._children.values():
                v.remove([], value)  # discard all in children
        elif key[0] == self.wildcard:
            if len(key) == 1:  # remove from self
                self._data.discard(value)
            for v in self._children.values():
                v.remove(key[1:], value)
        else:
            self._children[key[0]].remove(key[1:], value)

    @split_kwarg("key")
    def clear(self, key=None):
        if key is None or len(key) == 0:
            self._data.clear()
            self._children.clear()
        elif key[0] == self.wildcard:
            if len(key) == 1:  # clear self
                self.clear()
            else:  # clear children
                for v in self._children.values():
                    v.clear([key[1:]])
        else:
            self._children[key[0]].clear(key[1:])

    def is_leaf(self):
        return len(self._children) == 0

    def keys(self):
        for key, value in self._children.items():
            if len(value._data) > 0:
                yield key
            for ckey in value.keys():
                yield key + self.delim + ckey

    def __str__(self):
        return "(" + str(self._children) + ", " + str(self._data) + ")"

    def __repr__(self):
        return str(self)

    def values(self):
        result = self._data.copy()
        for v in self._children.values():
            result = result.union(v.values())
        return result

    def __len__(self):
        l = len(self._data)
        for v in self._children.values():
            l += len(v)
        return l

    @split_first_arg
    def __getitem__(self, key):
        if len(key) == 0:
            return self.values()
        elif key[0] == self.wildcard:
            result = (
                self._data if len(key) == 1 else set()
            )  # dont include self data if there are more keys to check
            for v in self._children.values():
                result = result.union(v[key[1:]])
            return result
        else:
            if key[0] in self._children:
                return self._children[key[0]][key[1:]]
            else:
                return set()  # key was not found...


if __name__ == "__main__":
    import unittest

    class TestEventDict(unittest.TestCase):
        def setUp(self):
            self.nested_dict = EventDict()

        def test_add_single_value(self):
            self.nested_dict.add("A::B::C", 1)
            self.assertEqual(self.nested_dict["A::B::C"], {1})

        def test_add_multiple_values(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::C", 2)
            self.assertEqual(self.nested_dict["A::B::C"], {1, 2})

        def test_add_global_value(self):
            self.nested_dict.add([], 1)
            self.assertEqual(self.nested_dict[[]], {1})

        def test_remove_single_value(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.remove("A::B::C", 1)
            self.assertEqual(self.nested_dict["A::B::C"], set())

        def test_remove_multiple_values1(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::C", 2)
            self.nested_dict.remove("A::B::C", 1)
            self.assertEqual(self.nested_dict["A::B::C"], {2})

        def test_remove_multiple_values2(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 1)
            self.nested_dict.remove("A::B", 1)
            self.assertEqual(self.nested_dict["A::B"], set())
            self.assertEqual(self.nested_dict["A::B::C"], set())
            self.assertEqual(self.nested_dict["A::B::D"], set())

        def test_remove_multiple_values_with_wildcard1(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 1)
            self.nested_dict.remove("A::B::*", 1)
            self.assertEqual(self.nested_dict["A::B"], set())
            self.assertEqual(self.nested_dict["A::B::C"], set())
            self.assertEqual(self.nested_dict["A::B::D"], set())

        def test_remove_multiple_values_with_wildcard2(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::C::C", 1)
            self.nested_dict.add("A::C::C", 2)
            self.nested_dict.remove("A::*::C", 1)
            self.assertEqual(self.nested_dict["A::B::C"], set())
            self.assertEqual(self.nested_dict["A::C::C"], {2})

        def test_clear(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 2)
            self.nested_dict.clear()
            self.assertEqual(self.nested_dict["A::B::C"], set())
            self.assertEqual(self.nested_dict["A::B::D"], set())

        def test_keys1(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 2)
            self.nested_dict.add("A::E::C", 3)
            keys = set(self.nested_dict.keys())
            expected_keys = {"A::B::C", "A::B::D", "A::E::C"}
            self.assertEqual(keys, expected_keys)

        def test_keys2(self):
            self.nested_dict.add("A::B", 0)
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 2)
            self.nested_dict.add("A::E::C", 3)
            keys = set(self.nested_dict.keys())
            expected_keys = {"A::B", "A::B::C", "A::B::D", "A::E::C"}
            self.assertEqual(keys, expected_keys)

        def test_keys_with_global(self):
            self.nested_dict.add([], 0)  # global...
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 2)
            self.nested_dict.add("A::E::C", 3)
            keys = set(self.nested_dict.keys())
            expected_keys = {"A::B::C", "A::B::D", "A::E::C"}
            self.assertEqual(keys, expected_keys)

        def test_values(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 2)
            self.nested_dict.add("A::E::C", 3)
            values = self.nested_dict.values()
            expected_values = {1, 2, 3}
            self.assertEqual(values, expected_values)

        def test_getitem(self):
            self.nested_dict.add("A::B::C", 1)
            self.nested_dict.add("A::B::D", 2)
            self.nested_dict.add("A::E::C", 3)
            self.assertEqual(self.nested_dict["A::B::C"], {1})
            self.assertEqual(self.nested_dict["A::*::C"], {1, 3})

    unittest.main()
