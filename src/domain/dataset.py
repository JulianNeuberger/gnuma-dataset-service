from typing import List, Optional
from uuid import uuid4, UUID

from eventsourcing.domain import Aggregate, AggregateCreated, AggregateEvent


class Dataset(Aggregate):
    def __init__(self, name, description: Optional[str] = '', field_mappings: Optional[List[UUID]] = None):
        self.name = name
        self.description = description
        self.train_validate_documents: List[str] = []
        self.test_documents: List[str] = []

        if field_mappings is None:
            self.field_mappings: List[UUID] = []
        else:
            self.field_mappings = field_mappings

        self.deleted = False

    @classmethod
    def create(cls, name: str, description: Optional[str]) -> 'Dataset':
        return cls._create(cls.Created, id=uuid4(), name=name, description=description)

    def add_train_documents(self, document_ids: List[str]):
        self.trigger_event(self.TrainDocumentsAddedEvent, document_ids=document_ids, dataset_id=self.id)

    def add_test_documents(self, document_ids: List[str]):
        self.trigger_event(self.TestDocumentsAddedEvent, document_ids=document_ids, dataset_id=self.id)

    def remove_train_documents(self, document_ids: List[str]):
        self.trigger_event(self.TrainDocumentsRemovedEvent, document_ids=document_ids, dataset_id=self.id)

    def remove_test_documents(self, document_ids: List[str]):
        self.trigger_event(self.TestDocumentsRemovedEvent, document_ids=document_ids, dataset_id=self.id)

    def update_meta(self, name: str, description: str):
        self.trigger_event(self.MetaDataUpdatedEvent, name=name, description=description)

    def update_mappings(self, mappings: List[UUID]):
        self.trigger_event(self.MappingsUpdatedEvent, mappings=mappings)

    def delete(self):
        self.trigger_event(self.Deleted)

    class Created(AggregateCreated):
        name: str
        description: str

    class Deleted(AggregateEvent):
        def apply(self, dataset: 'Dataset') -> None:
            dataset.deleted = True

    class TrainDocumentsRemovedEvent(AggregateEvent):
        document_ids: List[str]
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.train_validate_documents = [
                d
                for d in dataset.train_validate_documents
                if d not in self.document_ids
            ]

    class TestDocumentsRemovedEvent(AggregateEvent):
        document_ids: List[str]
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.test_documents = [
                d
                for d in dataset.test_documents
                if d not in self.document_ids
            ]

    class TrainDocumentsAddedEvent(AggregateEvent):
        document_ids: List[str]
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.train_validate_documents.extend(self.document_ids)

    class TestDocumentsAddedEvent(AggregateEvent):
        document_ids: List[str]
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.test_documents.extend(self.document_ids)

    class MetaDataUpdatedEvent(AggregateEvent):
        name: str
        description: str

        def apply(self, dataset: 'Dataset') -> None:
            dataset.name = self.name
            dataset.description = self.description

    class MappingsUpdatedEvent(AggregateEvent):
        mappings: List[UUID]

        def apply(self, dataset: 'Dataset') -> None:
            dataset.field_mappings = self.mappings
