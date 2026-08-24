import numpy as np

from exodynamics.uncertainty import split_normal_draws


def test_split_normal_is_bounded_and_reproducible() -> None:
    first = split_normal_draws(0.1, 0.2, 0.3, 100, lower=0, upper=1)
    second = split_normal_draws(0.1, 0.2, 0.3, 100, lower=0, upper=1)
    np.testing.assert_allclose(first, second)
    assert np.all((first >= 0) & (first <= 1))

