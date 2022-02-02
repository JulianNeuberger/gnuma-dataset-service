from typing import List, Optional, Iterable
from uuid import UUID

from eventsourcing.system import SingleThreadedRunner
from eventsourcing.system import System

from application.datasets import Datasets
from application.indices import ByDocumentIndices, DatasetIndices
from application.mappings import Mappings
from domain.dataset import Dataset
from domain.mapping import Mapping
from util import logwrapper


class DatasetsService:
    def __init__(self):
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Initializing dataset service...')

        # pipes are the concept of chains of aggregate
        # updates (events) triggered by a single event
        # at the head of a pipe. here: Inserting a
        # new document at a dataset will update the
        # "document -> dataset" index (pipe 1)
        # as well as the "all datasets" index (pipe 2)
        self._system = System(pipes=[
            [Datasets, ByDocumentIndices],  # pipe 1
            [Datasets, DatasetIndices],  # pipe 2
            [Mappings]
        ])
        self._runner = SingleThreadedRunner(self._system)
        self._runner.start()

    def shutdown(self):
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Shutting down dataset microservice...')
        self._runner.stop()

    def get_dataset(self, dataset_id: str) -> Dataset:
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Loading dataset with id {dataset_id}...')
        dataset_id = UUID(dataset_id)
        datasets = self._runner.get(Datasets)
        return datasets.get_dataset(dataset_id)

    # FIXME: paginate result
    def get_all_datasets(self) -> List[Dataset]:
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Loading all datasets...')
        indices = self._runner.get(DatasetIndices)
        datasets = self._runner.get(Datasets)
        dataset_ids = indices.get_all_dataset_ids()
        return [datasets.get_dataset(dataset_id) for dataset_id in dataset_ids]

    @staticmethod
    def get_mapping(mapping_id: str) -> Mapping:
        mappings = Mappings()
        return mappings.get_mapping(UUID(mapping_id))

    @staticmethod
    def get_mappings(mapping_ids: List[str]) -> Iterable[Mapping]:
        mappings = Mappings()
        return mappings.get_mappings([UUID(m) for m in mapping_ids])

    @staticmethod
    def get_mappings_for_dataset(dataset: Dataset) -> Iterable[Mapping]:
        mappings = Mappings()
        return mappings.get_mappings([m for m in dataset.field_mappings])

    def create_dataset(self, dataset_name: str, dataset_description: str = '') -> UUID:
        datasets = self._runner.get(Datasets)
        dataset_id = datasets.create_dataset(dataset_name, dataset_description)
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Created new dataset with id {dataset_id}...')
        return dataset_id

    def create_mapping(self, name: str, description: str, aliases: List[str], tasks: List[str]) -> UUID:
        mappings = Mappings()
        mapping_id = mappings.create_mapping(name, description, aliases, tasks)
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Created new mapping with id {mapping_id}...')
        return mapping_id

    def delete(self, dataset_id: str) -> None:
        datasets = self._runner.get(Datasets)
        datasets.delete_dataset(UUID(dataset_id))

    def update_meta(self, dataset_id: str, name: Optional[str], description: Optional[str]):
        datasets = self._runner.get(Datasets)
        datasets.update_meta(UUID(dataset_id), name, description)

    def update_mappings(self, dataset_id: str, mappings: List[str]):
        mappings = [UUID(m) for m in mappings]
        datasets = self._runner.get(Datasets)
        datasets.update_mappings(UUID(dataset_id), mappings)

    def add_train_documents_to_dataset(self, dataset_id: str, document_ids: List[str]):
        logwrapper.info(f'Dataset service [{hex(id(self))}]: '
                        f'Adding {len(document_ids)} train documents to dataset {dataset_id}...')
        datasets = self._runner.get(Datasets)
        datasets.add_train_documents(UUID(dataset_id), document_ids)

    def add_test_documents_to_dataset(self, dataset_id: str, document_ids: List[str]):
        logwrapper.info(f'Dataset service [{hex(id(self))}]: '
                        f'Adding {len(document_ids)} test documents to dataset {dataset_id}...')
        datasets = self._runner.get(Datasets)
        datasets.add_test_documents(UUID(dataset_id), document_ids)

    def remove_train_documents_from_dataset(self, dataset_id: str, document_ids: List[str]):
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Removing {len(document_ids)} '
                        f'train documents from dataset {dataset_id}...')
        datasets = self._runner.get(Datasets)
        datasets.remove_train_documents(UUID(dataset_id), document_ids)

    def remove_test_documents_from_dataset(self, dataset_id: str, document_ids: List[str]):
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Removing {len(document_ids)} '
                        f'test documents from dataset {dataset_id}...')
        datasets = self._runner.get(Datasets)
        datasets.remove_test_documents(UUID(dataset_id), document_ids)

    def remove_documents_from_all_datasets(self, document_ids: List[str]):
        logwrapper.info(f'Dataset service [{hex(id(self))}]: Removing {len(document_ids)} '
                        f'train and test documents from all datasets...')
        indices = self._runner.get(ByDocumentIndices)
        datasets = self._runner.get(Datasets)
        for document_id in document_ids:
            dataset_ids = indices.get_datasets_by_document(document_id)
            for dataset_id in dataset_ids:
                datasets.remove_train_documents(dataset_id, [document_id])
                datasets.remove_test_documents(dataset_id, [document_id])
