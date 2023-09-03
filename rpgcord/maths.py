import numpy as np
import random

from rpgcord.data.characteristic_data import characteristics


CMP_PIVOT = [random.random() for _ in characteristics]


def product_of_char_list(char_list: list[int]) -> float:
    mean = np.mean(char_list)
    chars = [char - mean for char in char_list]
    return np.dot(chars, CMP_PIVOT)
