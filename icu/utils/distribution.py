""" Utility module that defines different kinds of distributions that may be used in schedule files. 

For example:
```
    "!uniform(-5,5)"
```
The `!` is required to let the schedule parse know that this is not a `str` type. 
See scheduling documentation for further details. 
"""

import random
from typing import Callable, List
from .exception import ConfigurationError


def get_distribution_cls(name):
    """_summary_

    Args:
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    names = {
        k.__name__.lower(): k for k in Distribution.__subclasses__()
    }  # get all of the distribution sub-classes that have been defined
    return names.get(name, None)


class Distribution:
    """Base class for distributions."""

    def __call__(self):
        return self.sample()

    def sample(self):
        """Sample from this distribution."""
        raise NotImplementedError()


class Choice(Distribution):
    """A distribution that chooses a value uniformly from a collection."""

    def __init__(self, *choices: List[Callable]):
        """Construtor.
        Args:
            choices (*List[Callable]): arguments specifying the choice values. These should be [Callable] as they will be resolved on sample.
        """
        self.choices = tuple(choices)

    def sample(self):
        return random.choice([c() for c in self.choices])

    def __str__(self):
        return "choice" + str(self.choices)

    def __repr__(self):
        return str(self)


class Uniform(Distribution):
    """Uniform distribution."""

    def __init__(self, a, b):  # pylint: disable=C0103
        super().__init__()
        self.a = a  # pylint: disable=C0103
        self.b = b  # pylint: disable=C0103

    def _sample_float(self, a, b):  # pylint: disable=C0103
        return random.uniform(a, b)

    def _sample_int(self, a, b):  # pylint: disable=C0103
        return random.randint(a, b)

    def sample(self):
        a, b = self.a(), self.b()
        if isinstance(a, int) and isinstance(b, int):
            return self._sample_int(a, b)
        if isinstance(a, float) or isinstance(b, float):
            return self._sample_float(a, b)
        raise ConfigurationError(
            f"Invalid arguments for {Uniform} sampling after value resolution: {a}, {b}, must be numbers."
        )

    def __str__(self):
        return f"uniform({self.a},{self.b})"

    def __repr__(self):
        return str(self)


class Normal(Distribution):
    """Normal distribution."""

    def __init__(self, mu, sigma):  # pylint: disable=C0103
        super().__init__()
        self.mu = mu  # pylint: disable=C0103
        self.sigma = sigma

    def sample(self):
        mu, sigma = self.mu(), self.sigma()
        if isinstance(mu, (int, float)) and isinstance(sigma, (int, float)):
            return random.gauss(self.mu, self.sigma)
        else:
            raise ConfigurationError(
                f"Invalid arguments for {Normal} sampling after value resolution: {mu}, {sigma}, must be numbers."
            )

    def __str__(self):
        return f"normal({self.mu}, {self.sigma})"

    def __repr__(self):
        return str(self)
