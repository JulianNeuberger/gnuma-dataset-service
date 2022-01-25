from flask_hal.document import Document as HALDocument
from flask_hal.link import Link as HALLink, Collection as HALCollection

from domain.dataset import Dataset


def serialize_dataset(dataset: Dataset):
    return HALDocument(
        data={
            'id': dataset.id.hex,
            'name': dataset.name,
            'description': dataset.description,
            'documents': dataset.contained_documents
        },
        links=HALCollection(*map(lambda l: HALLink(rel='', href=l), dataset.contained_documents)),
    )
