import random

import numpy
from sklearn.model_selection import KFold

from domain.dataset import Dataset


def split_data(dataset: Dataset, num_folds: int = None, test_split: float = None,
               validate_split: float = None, seed: str = None):
    _train_data = dataset.train_validate_documents.copy()
    _test_data = dataset.test_documents.copy()

    # if a random seed is given use it to make splitting deterministic
    if seed is not None:
        random.seed(seed)

    # if a test split ratio is given create a random test set
    if test_split is not None:
        assert len(_test_data) == 0, 'Test split given for dataset that already has predefined test set'
        assert test_split > 0.0, f'The given ratio for test data ({test_split}) has to be greater than 0.'
        random.shuffle(_train_data)
        split_idx = int((1 - test_split) * len(_train_data))
        _train_data, _test_data = _train_data[:split_idx], _train_data[split_idx:]

    # if a number of folds is given create the folds
    if num_folds is not None:
        assert validate_split is None, 'Validate split given while expecting k-fold splits. ' \
                                       'These are mutually exclusive.'
        assert num_folds > 1, f'Can only create k-fold splits if number of folds is greater than 1, {num_folds} is given'
        _train_data = numpy.array(_train_data)
        _train_data = numpy.expand_dims(_train_data, axis=1)

        folds = []
        kf = KFold(num_folds)
        for i, (train_indices, validation_indices) in enumerate(kf.split(_train_data)):
            train_samples, validation_samples = _train_data[train_indices], _train_data[validation_indices]
            train_samples, validation_samples = numpy.squeeze(train_samples), numpy.squeeze(validation_samples)
            train_samples, validation_samples = train_samples.tolist(), validation_samples.tolist()
            folds.append({
                'train': train_samples,
                'valid': validation_samples
            })
        return folds, _test_data

    # if no k-fold splitting is requested then return a single "fold" containing all training data
    # and an optional validation data if validation ratio is given
    if validate_split is not None:
        assert validate_split > 0.0, f'The given ratio of validation data has to be greater than 0.'
        split_idx = int((1 - validate_split) * len(_train_data))
        _train_data, _valid_data = _train_data[:split_idx], _train_data[split_idx:]
        fold = {
            'train': _train_data,
            'valid': _valid_data
        }
    else:
        fold = {
            'train': _train_data
        }

    return [fold], _test_data
