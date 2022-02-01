from functools import singledispatchmethod
from typing import List, Union
from uuid import UUID

from eventsourcing.application import AggregateNotFound
from eventsourcing.domain import AggregateEvent
from eventsourcing.system import ProcessEvent, ProcessApplication

from domain.dataset import Dataset
from domain.index import ByDocumentIndex, DatasetIndex


class ByDocumentIndices(ProcessApplication):
    @singledispatchmethod
    def policy(self, domain_event: AggregateEvent, process_event: ProcessEvent) -> None:
        pass

    @policy.register(Dataset.TestDocumentsAddedEvent)
    @policy.register(Dataset.TrainDocumentsAddedEvent)
    def _add_document_to_index(self,
                               domain_event: Union[Dataset.TrainDocumentsAddedEvent, Dataset.TestDocumentsAddedEvent],
                               process_event: ProcessEvent):
        assert isinstance(domain_event, Dataset.TrainDocumentsAddedEvent) or \
               isinstance(domain_event, Dataset.TestDocumentsAddedEvent)
        for document_id in domain_event.document_ids:
            index_id = ByDocumentIndex.create_id(document_id)
            try:
                index: ByDocumentIndex = self.repository.get(index_id)
            except AggregateNotFound:
                index: ByDocumentIndex = ByDocumentIndex.create(document_id)
            index.add_dataset_to_index(domain_event.dataset_id)
            process_event.save(index)

    @policy.register(Dataset.SingleDocumentOfTypeRemovedEvent)
    @policy.register(Dataset.AllDocumentsOfTypeRemovedEvent)
    def _remove_document_from_index(self,
                                    domain_event: Union[Dataset.SingleDocumentOfTypeRemovedEvent,
                                                        Dataset.AllDocumentsOfTypeRemovedEvent],
                                    process_event: ProcessEvent):
        assert isinstance(domain_event, Dataset.SingleDocumentOfTypeRemovedEvent) or \
               isinstance(domain_event, Dataset.AllDocumentsOfTypeRemovedEvent)
        index_id = ByDocumentIndex.create_id(domain_event.document_id)
        try:
            index: ByDocumentIndex = self.repository.get(index_id)
            index.remove_dataset_from_index(domain_event.dataset_id)
            process_event.save(index)
        except AggregateNotFound:
            return

    def create_index(self, document_id: str) -> UUID:
        index = ByDocumentIndex.create(document_id)
        self.save(index)
        return index.id

    def get_datasets_by_document(self, document_id: str) -> List[UUID]:
        index_id = ByDocumentIndex.create_id(document_id)
        try:
            index: ByDocumentIndex = self.repository.get(index_id)
            return list(index.datasets)
        except AggregateNotFound:
            return []

    def get_index(self, index_id: UUID):
        return self.repository.get(index_id)


class DatasetIndices(ProcessApplication):
    @singledispatchmethod
    def policy(self, domain_event: AggregateEvent, process_event: ProcessEvent) -> None:
        pass

    @policy.register(Dataset.Created)
    def _add_dataset_to_index(self, domain_event: Dataset.Created, process_event: ProcessEvent):
        assert isinstance(domain_event, Dataset.Created)
        index_id = DatasetIndex.create_id()
        try:
            index: DatasetIndex = self.repository.get(index_id)
        except AggregateNotFound:
            index: DatasetIndex = DatasetIndex.get()
        index.add_dataset_to_index(domain_event.originator_id)
        process_event.save(index)

    @policy.register(Dataset.Deleted)
    def _remove_dataset_from_index(self, domain_event: Dataset.Deleted, process_event: ProcessEvent):
        assert isinstance(domain_event, Dataset.Deleted)
        index_id = DatasetIndex.create_id()
        try:
            index: DatasetIndex = self.repository.get(index_id)
        except AggregateNotFound:
            index: DatasetIndex = DatasetIndex.get()
        index.remove_dataset_from_index(domain_event.originator_id)
        process_event.save(index)

    def create_index(self) -> UUID:
        index = DatasetIndex.get()
        self.save(index)
        return index.id

    def get_all_dataset_ids(self) -> List[UUID]:
        index_id = DatasetIndex.create_id()
        try:
            index: DatasetIndex = self.repository.get(index_id)
            return list(index.datasets)
        except AggregateNotFound:
            return []

    def get_index(self, index_id: UUID):
        return self.repository.get(index_id)
