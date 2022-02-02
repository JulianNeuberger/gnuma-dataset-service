from collections import Counter
from typing import Iterable, Any, Dict, List

from eventsourcing.application import AggregateNotFound
from flask import request, jsonify
from flask_restful import abort, Resource
from marshmallow import Schema, fields, ValidationError
from marshmallow.validate import Range, Length

from api.schemas import DatasetQuerySchema, DatasetPatchSchema, DatasetCreationSchema
from domain.dataset import Dataset
from interface.service import DatasetsService
from serializer import serialize_dataset


def abort_not_json():
    abort(400, message='Only accepting requests with mime type application/json.')


def abort_missing_parameter(parameter_name: str):
    abort(400, message=f'Expected "{parameter_name}" to be part of the request body.')


def diff(a: Iterable, b: Iterable) -> Iterable:
    """
    Calculates the asymmetric difference c between lists a and b,
    so that a + c = b.

    E.g.:
    ```
    > a = [1, 2, 3]
    > b = [2, 3]
    > c = diff(a, b)
    > print(c)
    [1]

    > a = [1, 2, 3]
    > b = [2, 3]
    > c = diff(b, a)
    > print(c)
    []

    > a = [1, 1, 1, 1]
    > b = [2, 2, 2, 2]
    > c = diff(a, b)
    > print(c)
    [1, 1, 1, 1]
    ```

    :param a: an iterable of hashable values
    :param b: an iterable of hashable values
    :return: the difference as iterable of differing values
    """
    a_counter = Counter(a)
    b_counter = Counter(b)

    difference = a_counter - b_counter

    return list(difference.elements())


class DebugDocumentRemover(Resource):
    def __init__(self, datasets_service: DatasetsService):
        print(f'Initializing API resource {self.__class__.__name__} with dataset service {hex(id(datasets_service))}')
        self._datasets_service = datasets_service

    def delete(self, document_id):
        self._datasets_service.remove_document_from_all_datasets(document_id)
        return jsonify({
            'success': True
        })


def update_documents(dataset_id: str, new_documents: List[str], old_documents: List[str],
                     update_method, datasets_service: DatasetsService):
    added_documents = diff(new_documents, old_documents)
    removed_documents = diff(old_documents, new_documents)

    for document in added_documents:
        update_method(dataset_id, document)

    for document in removed_documents:
        datasets_service.remove_document_from_dataset(dataset_id, document)


def patch_dataset(params: Dict[str, Any], dataset: Dataset, datasets_service: DatasetsService):
    if 'train_documents' in params:
        old_documents = dataset.train_validate_documents
        new_documents = params['train_documents']
        update_documents(dataset.id.hex, new_documents, old_documents,
                         datasets_service.add_train_document_to_dataset, datasets_service)

    if 'test_documents' in params:
        old_documents = dataset.test_documents
        new_documents = params['test_documents']
        update_documents(dataset.id.hex, new_documents, old_documents,
                         datasets_service.add_test_document_to_dataset, datasets_service)

    if 'name' in params or 'description' in params:
        name = params.get('name', None)
        description = params.get('description', None)
        datasets_service.update_meta(dataset.id.hex, name, description)

    if 'mappings' in params:
        mapping_ids = []
        for mapping in params['mappings']:
            mapping_id = datasets_service.create_mapping(mapping['name'], mapping['description'],
                                                         mapping['aliases'], mapping['tasks'])
            mapping_ids.append(str(mapping_id))
        datasets_service.update_mappings(dataset.id.hex, mapping_ids)


class Dataset(Resource):
    def __init__(self, datasets_service: DatasetsService):
        print(f'Initializing API resource {self.__class__.__name__} with dataset service {hex(id(datasets_service))}')
        self._datasets_service = datasets_service

    def get(self, dataset_id):
        dataset = self._datasets_service.get_dataset(dataset_id)
        mappings = self._datasets_service.get_mappings_for_dataset(dataset)

        try:
            params = DatasetQuerySchema().load(request.args)
        except ValidationError as e:
            return e.messages, 400

        if params.get('test_split') is not None and len(dataset.test_documents) > 0:
            return 'Got a test split ratio of document with predefined test set.', 400

        if params.get('validation_split') is not None and params.get('k_folds') is not None:
            return 'Both a validation and a k-fold split is requested, these are mutually exclusive.', 400

        hal_document = serialize_dataset(dataset, mappings,
                                         params.get('k_folds'), params.get('test_split'),
                                         params.get('validation_split'), params.get('seed'))

        return jsonify(hal_document.to_dict())

    def patch(self, dataset_id):
        if not request.is_json:
            return abort_not_json()

        try:
            params = DatasetPatchSchema().load(request.json, unknown='EXCLUDE')
        except ValidationError as e:
            return e.messages, 400

        try:
            dataset = self._datasets_service.get_dataset(dataset_id)
        except AggregateNotFound:
            return f'No dataset with id {dataset_id}', 400

        patch_dataset(params, dataset, self._datasets_service)

        # TODO: here would be a good time to snapshot (?)

        dataset = self._datasets_service.get_dataset(dataset_id)
        mappings = self._datasets_service.get_mappings_for_dataset(dataset)

        return jsonify(serialize_dataset(dataset, mappings).to_dict())

    def delete(self, dataset_id):
        self._datasets_service.delete(dataset_id)


class DatasetList(Resource):
    def __init__(self, datasets_service: DatasetsService):
        print(f'Initializing API resource {self.__class__.__name__} with dataset service {hex(id(datasets_service))}')
        self._datasets_service = datasets_service

    def get(self):
        datasets = self._datasets_service.get_all_datasets()

        return jsonify([
            serialize_dataset(dataset, self._datasets_service.get_mappings_for_dataset(dataset)).to_dict()
            for dataset
            in datasets
        ])

    def post(self):
        if not request.is_json:
            return abort_not_json()

        try:
            params = DatasetCreationSchema().load(request.json, unknown='EXCLUDE')
        except ValidationError as e:
            return e.messages, 400

        dataset_id = self._datasets_service.create_dataset(params['name'], params['description'])
        dataset = self._datasets_service.get_dataset(dataset_id.hex)

        patch_dataset(params, dataset, self._datasets_service)

        # FIXME: generate uri properly (how?)
        return jsonify({
            'dataset': f'/datasets/{dataset_id}'
        })
