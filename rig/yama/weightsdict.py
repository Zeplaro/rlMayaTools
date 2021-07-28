from __future__ import division
import json


class WeightsDict(dict):
    def __init__(self, *args, **kwargs):
        super(WeightsDict, self).__init__()
        new = dict(*args, **kwargs)
        for i in new:
            self[i] = new[i]

    @staticmethod
    def _check(key, value=None, check_value=True):
        if not isinstance(key, int):
            try:
                key = int(key)
            except ValueError:
                raise ValueError('key must be int or digit str, Got : {} of type {}'.format(key, type(key).__name__))
        if check_value and not isinstance(value, float):
            try:
                value = float(value)
            except ValueError:
                raise ValueError('key must be int or digit str, Got : {} of type {}'.format(value, type(value).__name__))
        return key, value

    def __getitem__(self, item):
        item, _ = self._check(item, check_value=False)
        return super(WeightsDict, self).__getitem__(item)

    def __setitem__(self, key, value):
        key, value = self._check(key, value)
        super(WeightsDict, self).__setitem__(key, value)

    def get(self, k, value=None):
        k, _ = self._check(k, check_value=False)
        return super(WeightsDict, self).get(k, value)

    def __add__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] + other[j]
        return weights

    def __iadd__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        for i, j in zip(self, other):
            self[i] += other[j]

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] - other[j]
        return weights

    def __isub__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        for i, j in zip(self, other):
            self[i] -= other[j]

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] * other[j]
        return weights

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        for i, j in zip(self, other):
            self[i] *= other[j]

    def __div__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] / other[j]
        return weights

    def __idiv__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        for i, j in zip(self, other):
            self[i] /= other[j]

    def __neg__(self):
        weights = WeightsDict()
        for i in self:
            weights[i] = -self[i]
        return weights

    def __invert__(self):
        weights = WeightsDict()
        for i in self:
            weights[i] = 1 - self[i]
        return weights

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            other = weightsdict_from_float(other, len(self))
        if len(self) != len(other):
            return False
        for i in self:
            if not self[i] == other.get(i, None):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self[x] for x in range(len(self)))

    def __iter__(self):
        for i in range(len(self)):
            yield i

    def clamp(self, min_value=0.0, max_value=1.0):
        for i in self:
            if not max_value > self[i] > min_value:
                self[i] = max(min(self[i], max_value), min_value)

    def export_weights(self, path):
        export_weights(self, path)

    def import_weigths(self, path, apply_data=True):
        data = import_weights(path)
        if apply_data:
            for i in self:
                self[i] = data.get(i, self[i])
        return data


def normalize_weights(*weights):
    for i in weights:
        if not isinstance(i, WeightsDict):
            raise ValueError("Weights must be of type 'WeightsDict' not '{}'".format(type(i).__name__))
    dicts = [WeightsDict() for _ in range(len(weights))]
    for i in range(min(len(x) for x in weights)):
        mult = 1.0
        values = [x.get(i) for x in weights]
        if any(values):
            mult = 1.0 / sum(values)
        for d, w in zip(dicts, weights):
            d[i] = w[i] * mult
    return dicts


def weightsdict_from_float(value, length):
    return WeightsDict({i: value for i in range(length)})


def export_weights(data, path):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def import_weights(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data
