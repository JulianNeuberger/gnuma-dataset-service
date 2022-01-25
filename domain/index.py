from typing import Set
from uuid import uuid5, NAMESPACE_URL, UUID

from eventsourcing.domain import Aggregate, AggregateEvent, AggregateCreated


class ByDocumentIndex(Aggregate):
    def __init__(self):
        self.datasets: Set[UUID] = set()

    @classmethod
    def create_id(cls, document_id):
        return uuid5(NAMESPACE_URL, f'/index/document/{document_id}')

    @classmethod
    def create(cls, document_id: str) -> 'ByDocumentIndex':
        index_id = cls.create_id(document_id)
        return cls._create(cls.Created, id=index_id)

    def add_dataset_to_index(self, dataset_id: UUID):
        self.trigger_event(self.DatasetAddedEvent, dataset_id=dataset_id)

    def remove_dataset_from_index(self, dataset_id: UUID):
        self.trigger_event(self.DatasetRemovedEvent, dataset_id=dataset_id)

    class Created(AggregateCreated):
        pass

    class DatasetAddedEvent(AggregateEvent):
        dataset_id: UUID

        def apply(self, index: 'ByDocumentIndex') -> None:
            index.datasets.add(self.dataset_id)

    class DatasetRemovedEvent(AggregateEvent):
        dataset_id: UUID

        def apply(self, index: 'ByDocumentIndex') -> None:
            if self.dataset_id in index.datasets:
                index.datasets.remove(self.dataset_id)


class DatasetIndex(Aggregate):
    def __init__(self):
        self.datasets: Set[UUID] = set()

    @classmethod
    def create_id(cls):
        return uuid5(NAMESPACE_URL, f'/index/datasets')

    @classmethod
    def get(cls) -> 'DatasetIndex':
        index_id = cls.create_id()
        return cls._create(cls.Created, id=index_id)

    def add_dataset_to_index(self, dataset_id: UUID):
        self.trigger_event(self.DatasetAddedEvent, dataset_id=dataset_id)

    def remove_dataset_from_index(self, dataset_id: UUID):
        self.trigger_event(self.DatasetRemovedEvent, dataset_id=dataset_id)

    class Created(AggregateCreated):
        pass

    class DatasetAddedEvent(AggregateEvent):
        dataset_id: UUID

        def apply(self, index: 'DatasetIndex') -> None:
            index.datasets.add(self.dataset_id)

    class DatasetRemovedEvent(AggregateEvent):
        dataset_id: UUID

        def apply(self, index: 'DatasetIndex') -> None:
            if self.dataset_id in index.datasets:
                index.datasets.remove(self.dataset_id)