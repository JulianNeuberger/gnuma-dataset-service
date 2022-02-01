from collections import Counter
from typing import Iterable

from eventsourcing.application import AggregateNotFound
from flask import request, jsonify
from flask_restful import abort, Resource
from marshmallow import Schema, fields, ValidationError
from marshmallow.validate import Range

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


class DatasetQuerySchema(Schema):
    k_folds = fields.Integer(strict=False, required=False, data_key='kFolds', validate=Range(min=1))
    test_split = fields.Float(strict=True, required=False, data_key='testSplit',
                              validate=Range(min=0.0, max=1.0, min_inclusive=False, max_inclusive=False))
    validation_split = fields.Float(strict=True, required=False, data_key='validationSplit',
                                    validate=Range(min=0.0, max=1.0, min_inclusive=False, max_inclusive=False))
    seed = fields.String(strict=False, required=False,  data_key='seed')


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

        body = request.json

        try:
            dataset = self._datasets_service.get_dataset(dataset_id)
        except AggregateNotFound:
            return abort(404)

        if 'trainDocuments' in body:
            old_documents = dataset.train_validate_documents
            new_documents = body['trainDocuments']
            self._update_documents(dataset_id, new_documents, old_documents,
                                   self._datasets_service.add_train_document_to_dataset)

        if 'testDocuments' in body:
            old_documents = dataset.test_documents
            new_documents = body['testDocuments']
            self._update_documents(dataset_id, new_documents, old_documents,
                                   self._datasets_service.add_test_document_to_dataset)

        if 'name' in body or 'description' in body:
            name = body.get('name', None)
            description = body.get('description', None)
            self._datasets_service.update_meta(dataset_id, name, description)

        dataset = self._datasets_service.get_dataset(dataset_id)
        mappings = self._datasets_service.get_mappings_for_dataset(dataset)

        # TODO: here would be a good time to snapshot (?)

        return jsonify(serialize_dataset(dataset, mappings).to_dict())

    def delete(self, dataset_id):
        self._datasets_service.delete(dataset_id)

    def _update_documents(self, dataset_id, new_documents, old_documents, update_method):
        if type(new_documents) is not list:
            abort(400, message='Expected body attribute "documents" to be a list of document ids.')

        if len(new_documents) > 0 and type(new_documents[0]) is not str:
            abort(400, message='Expected document ids in "documents" to be a list of strings.')

        added_documents = diff(new_documents, old_documents)
        removed_documents = diff(old_documents, new_documents)

        for document in added_documents:
            update_method(dataset_id, document)

        for document in removed_documents:
            self._datasets_service.remove_document_from_dataset(dataset_id, document)


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

        body = request.json
        if 'name' not in body:
            return abort_missing_parameter('name')

        dataset_name = body['name']
        dataset_description = ''
        if 'description' in body:
            dataset_description = body['description']
        dataset_id = self._datasets_service.create_dataset(dataset_name, dataset_description)
        dataset_id = dataset_id.hex

        if 'trainDocuments' in body:
            for document in body['trainDocuments']:
                self._datasets_service.add_train_document_to_dataset(dataset_id, document)

        if 'testDocuments' in body:
            for document in body['testDocuments']:
                self._datasets_service.add_test_document_to_dataset(dataset_id, document)

        if 'mappings' in body:
            mapping_ids = []
            for mapping in body['mappings']:
                mapping_id = self._datasets_service.create_mapping(mapping['name'], mapping['description'],
                                                                   mapping['aliases'], mapping['tasks'])
                mapping_ids.append(str(mapping_id))
            self._datasets_service.update_mappings(dataset_id, mapping_ids)

        # FIXME: generate uri properly (how?)
        return jsonify({
            'dataset': f'/datasets/{dataset_id}'
        })
