from typing import List, Optional
from uuid import uuid4, UUID

from eventsourcing.domain import Aggregate, AggregateCreated, AggregateEvent


class Dataset(Aggregate):
    def __init__(self, name, description: Optional[str] = ''):
        self.name = name
        self.description = description
        self.contained_documents: List[str] = []
        self.deleted = False

    @classmethod
    def create(cls, name: str, description: Optional[str]) -> 'Dataset':
        return cls._create(cls.Created, id=uuid4(), name=name, description=description)

    def add_document(self, document_id: str):
        self.trigger_event(self.DocumentAddedEvent, document_id=document_id, dataset_id=self.id)

    def remove_document(self, document_id: str, single=True):
        if single:
            self.trigger_event(self.SingleDocumentOfTypeRemovedEvent, document_id=document_id, dataset_id=self.id)
        else:
            self.trigger_event(self.AllDocumentsOfTypeRemovedEvent, document_id=document_id, dataset_id=self.id)

    def update_meta(self, name: str, description: str):
        self.trigger_event(self.MetaDataUpdatedEvent, name=name, description=description)

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
            if self.document_id in dataset.contained_documents:
                dataset.contained_documents.remove(self.document_id)

    class AllDocumentsOfTypeRemovedEvent(AggregateEvent):
        document_id: str
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.contained_documents = [d for d in dataset.contained_documents if d != self.document_id]

    class DocumentAddedEvent(AggregateEvent):
        document_id: str
        dataset_id: UUID

        def apply(self, dataset: 'Dataset') -> None:
            dataset.contained_documents.append(self.document_id)

    class MetaDataUpdatedEvent(AggregateEvent):
        name: str
        description: str

        def apply(self, dataset: 'Dataset') -> None:
            dataset.name = self.name
            dataset.description = self.description