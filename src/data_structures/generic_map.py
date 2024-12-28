from typing import TypeVar, Generic

K = TypeVar("K") # Type for the key
V = TypeVar("V") # Type for the value

class GenericMap(Generic[K, V]):
    def __init__(self):
        self._map: dict[K, V] = {}

    def add(self, key: K, value: V) -> None:
        self._map[key] = value

    def remove(self, key: K) -> None:
        if key in self._map:
            del self._map[key]

    def remove_and_get(self, key: K):
        val = self.get(key)
        if val != None:
            del self._map[key]
            return (key, val)

    def get(self, key: K) -> V | None:
        return self._map.get(key)

    def get_keys(self):
        return list(self._map.keys())

    def get_values(self):
        return list(self._map.values())

    def get_items(self):
        return list(self._map.items())

    def clear(self):
        self._map.clear()
