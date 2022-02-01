from typing import Iterable

from flask_hal.document import Document as HALDocument, Embedded
from flask_hal.link import Link as HALLink, Collection as HALCollection

from domain.dataset import Dataset
from domain.mapping import Mapping
from util.datasplitter import split_data


def serialize_mapping(mapping: Mapping) -> HALDocument:
    return HALDocument(
        data={
            'name': mapping.name,
            'description': mapping.description,
            'aliases': mapping.aliases,
            'tasks': mapping.tasks
        }
    )


def serialize_dataset(dataset: Dataset, mappings: Iterable[Mapping],
                      num_folds: int = None, test_split: float = None,
                      valid_split: float = None, seed: str = None) -> HALDocument:
    folds, test_data = split_data(dataset, num_folds, test_split, valid_split, seed)

    data_info = {}
    if num_folds is not None:
        data_info['kFolds'] = num_folds
    if test_split is not None:
        data_info['testSplit'] = test_split
    if valid_split is not None:
        data_info['validationSplit'] = valid_split
    if seed is not None:
        data_info['seed'] = seed

    data = {
        'folds': folds
    }
    if len(test_data) > 0:
        data['test'] = test_data

    return HALDocument(
        data={
            **data_info,
            'id': dataset.id.hex,
            'name': dataset.name,
            'description': dataset.description,
            'data': data
        },
        embedded={
            'mappings': Embedded(
                data=[serialize_mapping(m) for m in mappings]
            )
        },
        links=HALCollection(*map(lambda l: HALLink(rel='', href=l), dataset.train_validate_documents)),
    )
