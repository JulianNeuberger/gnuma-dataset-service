import logging
from typing import List, Optional
from uuid import UUID

from eventsourcing.system import SingleThreadedRunner
from eventsourcing.system import System

from application.datasets import Datasets
from application.indices import ByDocumentIndices, DatasetIndices
from domain.dataset import Dataset


class DatasetsService:
    def __init__(self):
        logging.info(f'Dataset service [{hex(id(self))}]: Initializing dataset service...')

        # pipes are the concept of chains of aggregate
        # updates (events) triggered by a single event
        # at the head of a pipe. here: Inserting a
        # new document at a dataset will update the
        # "document -> dataset" index (pipe 1)
        # as well as the "all datasets" index (pipe 2)
        self._system = System(pipes=[
            [Datasets, ByDocumentIndices],  # pipe 1
            [Datasets, DatasetIndices]  # pipe 2
        ])
        self._runner = SingleThreadedRunner(self._system)
        self._runner.start()

    def shutdown(self):
        logging.info(f'Dataset service [{hex(id(self))}]: Shutting down dataset microservice...')
        self._runner.stop()

    def get_one(self, dataset_id: str) -> Dataset:
        logging.info(f'Dataset service [{hex(id(self))}]: Loading dataset with id {dataset_id}...')
        dataset_id = UUID(dataset_id)
        datasets = self._runner.get(Datasets)
        return datasets.get_dataset(dataset_id)

    # FIXME: paginate result
    def get_all(self) -> List[Dataset]:
        logging.info(f'Dataset service [{hex(id(self))}]: Loading all datasets...')
        indices = self._runner.get(DatasetIndices)
        datasets = self._runner.get(Datasets)
        dataset_ids = indices.get_all_dataset_ids()
        return [datasets.get_dataset(dataset_id) for dataset_id in dataset_ids]

    def create(self, dataset_name: str, dataset_description: str = '') -> UUID:
        datasets = self._runner.get(Datasets)
        dataset_id = datasets.create_dataset(dataset_name, dataset_description)
        logging.info(f'Dataset service [{hex(id(self))}]: Created new dataset with id {dataset_id}...')
        return dataset_id

    def delete(self, dataset_id: str) -> None:
        datasets = self._runner.get(Datasets)
        datasets.delete_dataset(UUID(dataset_id))

    def update_meta(self, dataset_id: str, name: Optional[str], description: Optional[str]):
        datasets = self._runner.get(Datasets)
        datasets.update_meta(UUID(dataset_id), name, description)

    def add_document_to_dataset(self, dataset_id: str, document_id: str):
        logging.info(f'Dataset service [{hex(id(self))}]: Adding document {document_id} to dataset {dataset_id}...')
        datasets = self._runner.get(Datasets)
        datasets.add_document(UUID(dataset_id), document_id)

    def remove_document_from_dataset(self, dataset_id: str, document_id: str, single=True):
        logging.info(
            f'Dataset service [{hex(id(self))}]: Removing {"one" if single else "all"} document {document_id} from dataset {dataset_id}...')
        datasets = self._runner.get(Datasets)
        datasets.remove_document(UUID(dataset_id), document_id, single=single)

    def remove_document_from_all_datasets(self, document_id: str, single=True):
        logging.info(
            f'Dataset service [{hex(id(self))}]: Removing {"one" if single else "all"} document {document_id} from all datasets...')
        indices = self._runner.get(ByDocumentIndices)
        datasets = self._runner.get(Datasets)
        dataset_ids = indices.get_datasets_by_document(document_id)
        for dataset_id in dataset_ids:
            datasets.remove_document(dataset_id, document_id, single=single)
