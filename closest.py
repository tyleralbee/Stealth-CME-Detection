import numpy as np

__author__ = "James Paul Mason"
__contact__ = "jmason86@gmail.com"


def closest(array, target):
    """Get the closest index in an array.

    Inputs:
        array [np.array]: The array to search.
        target [number]:  The number you're looking for. Can be int, float, double.

    Optional Inputs:
        None

    Outputs:
        index [int]: The index in the array that corresponds to the closest value to target.

    Optional Outputs:
        None

    Example:
        closest_index = closest(nd.arange(0, 10), 4.3)
    """
    return np.argmin(np.abs(array - target))
