from __future__ import division


class WeightsDict(dict):
    def __init__(self, *args, **kwargs):
        super(WeightsDict, self).__init__()
        new = dict(*args, **kwargs)
        for k, v in new.items():
            self[k] = v

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
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] + other[j]
        return weights

    def __iadd__(self, other):
        for i, j in zip(self, other):
            self[i] += other[j]

    def __sub__(self, other):
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] - other[j]
        return weights

    def __isub__(self, other):
        for i, j in zip(self, other):
            self[i] -= other[j]

    def __mul__(self, other):
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] * other[j]
        return weights

    def __imul__(self, other):
        for i, j in zip(self, other):
            self[i] *= other[j]

    def __div__(self, other):
        weights = WeightsDict()
        for i, j in zip(self, other):
            weights[i] = self[i] / other[j]
        return weights

    def __idiv__(self, other):
        for i, j in zip(self, other):
            self[i] /= other[j]

    def __neg__(self):
        for i in self:
            self[i] = -self[i]

    def __invert__(self):
        for i in self:
            self[i] = 1 - self[i]

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in self:
            if not self[i] == other.get(i, None):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def normalize(self, weights):
        dicts = WeightsDict(), WeightsDict()
        for (i, weight_i), (j, weight_j) in zip(self.items(), weights.items()):
            mult = 1.0
            if weight_i or weight_j:
                mult = 1.0 / (weight_i + weight_j)
            # if mult != 1.0 and mult != 0.0:
            #     print(weight_i, weight_j, mult)
            #     print(weight_i*mult)
            dicts[0][i] = weight_i * mult
            dicts[1][j] = weight_j * mult
        return dicts
