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

    def add_train_document(self, document_id: str):
        self.trigger_event(self.TrainDocumentAddedEvent, document_id=document_id, dataset_id=self.id)

    def add_test_document(self, document_id: str):
        self.trigger_event(self.TestDocumentAddedEvent, document_id=document_id, dataset_id=self.id)

    def remove_document(self, document_id: str, single=True):
        if single:
            self.trigger_event(self.SingleDocumentOfTypeRemovedEvent, document_id=document_id, dataset_id=self.id)
        else:
            self.trigger_event(self.AllDocumentsOfTypeRemovedEvent, document_id=document_id, dataset_id=self.id)

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

    class SingleDocumentOfTypeRemovedEvent(AggregateEvent):
        document_id: str
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            if self.document_id in dataset.train_validate_documents:
                dataset.train_validate_documents.remove(self.document_id)
            if self.document_id in dataset.test_documents:
                dataset.test_documents.remove(self.document_id)

    class AllDocumentsOfTypeRemovedEvent(AggregateEvent):
        document_id: str
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.train_validate_documents = [d for d in dataset.train_validate_documents if d != self.document_id]
            dataset.test_documents = [d for d in dataset.test_documents if d != self.document_id]

    class TrainDocumentAddedEvent(AggregateEvent):
        document_id: str
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.train_validate_documents.append(self.document_id)

    class TestDocumentAddedEvent(AggregateEvent):
        document_id: str
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.test_documents.append(self.document_id)

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
