from typing import Iterable

from flask_hal.document import Document as HALDocument, Embedded
from flask_hal.link import Link as HALLink, Collection as HALCollection

from domain.dataset import Dataset
from domain.mapping import Mapping


def serialize_mapping(mapping: Mapping) -> HALDocument:
    return HALDocument(
        data={
            'name': mapping.name,
            'description': mapping.description,
            'aliases': mapping.aliases,
            'tasks': mapping.tasks
        }
    )


def serialize_dataset(dataset: Dataset, mappings: Iterable[Mapping]) -> HALDocument:
    return HALDocument(
        data={
            'id': dataset.id.hex,
            'name': dataset.name,
            'description': dataset.description,
            'documents': dataset.contained_documents
        },
        embedded={
            'mappings': Embedded(
                data=[serialize_mapping(m) for m in mappings]
            )
        },
        links=HALCollection(*map(lambda l: HALLink(rel='', href=l), dataset.contained_documents)),
    )
