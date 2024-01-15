import typing

import numpy as np

# By gpt-4

def gapped_data_splitter(array: np.ndarray, test_size: float, gap_size: int) -> typing.Dict[str, np.ndarray]:
    """
    Splits a numpy array into training and testing sets with a gap between them.

    :param array: Input numpy array.
    :param test_size: Fraction of the dataset to include in the test split.
    :param gap_size: Size of the gap between training and testing sets.
    :return: Training set, Testing set
    """
    if not 0 < test_size < 1:
        raise ValueError("Test size should be a fraction between 0 and 1.")

    if not isinstance(gap_size, int) or gap_size < 0:
        raise ValueError("Gap size should be a non-negative integer.")

    total_size = len(array)
    test_set_size = int(np.floor(total_size * test_size))
    train_set_size = total_size - test_set_size - gap_size

    if train_set_size <= 0 or train_set_size + gap_size + test_set_size > total_size:
        raise ValueError("Invalid combination of test size and gap size for the given array.")

    train_set = array[:train_set_size]
    test_set = array[train_set_size + gap_size:]

    return {'train': train_set, 'test': test_set}


def gapped_cv_data_splitter(array, num_folds: int, gap_size: int, test_size: float) -> typing.List[dict]:
    if not 1 < num_folds <= len(array):
        raise ValueError("Number of folds must be at least 2 and at most the length of the array.")

    datasets_all = []
    fold_size = int(np.floor((len(array) - (num_folds - 1) * gap_size) / num_folds))
    
    if fold_size <= 0:
        raise ValueError("Fold size is too small for the given number of folds and gap size.")

    for fold_index in range(num_folds):
        fold_start = fold_index
        fold_end = fold_index + fold_size + gap_size
        datasets = gapped_data_splitter(
            array=array[fold_start:fold_end],
            test_size=test_size,
            gap_size=gap_size,
        )
        datasets_all.append(datasets)
    return datasets_all