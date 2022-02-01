from typing import Optional, List
from uuid import UUID

from eventsourcing.application import Application

from domain.dataset import Dataset


class Datasets(Application):
    def create_dataset(self, name: str, description: Optional[str] = '') -> UUID:
        dataset = Dataset.create(name, description)
        self.save(dataset)
        return dataset.id

    def get_dataset(self, dataset_id: UUID) -> Dataset:
        return self.repository.get(dataset_id)

    def delete_dataset(self, dataset_id: UUID) -> None:
        dataset: Dataset = self.repository.get(dataset_id)
        dataset.delete()
        self.save(dataset)

    def add_train_document(self, dataset_id: UUID, document_id: str):
        dataset: Dataset = self.repository.get(dataset_id)
        dataset.add_train_document(document_id)
        self.save(dataset)

    def add_test_document(self, dataset_id: UUID, document_id: str):
        dataset: Dataset = self.repository.get(dataset_id)
        dataset.add_test_document(document_id)
        self.save(dataset)

    def remove_document(self, dataset_id: UUID, document_id: str, single=True):
        dataset: Dataset = self.repository.get(dataset_id)
        dataset.remove_document(document_id, single)
        self.save(dataset)

    def update_meta(self, dataset_id: UUID, name: Optional[str], description: Optional[str]):
        dataset: Dataset = self.repository.get(dataset_id)
        if name is None:
            name = dataset.name
        if description is None:
            description = dataset.description
        dataset.update_meta(name, description)
        self.save(dataset)

    def update_mappings(self, dataset_id: UUID, mappings: List[UUID]):
        dataset: Dataset = self.repository.get(dataset_id)
        dataset.update_mappings(mappings)
        self.save(dataset)
