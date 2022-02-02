from unittest import TestCase

from application.datasets import Datasets
from application.indices import ByDocumentIndices


class TestDatasetAggregate(TestCase):
    def test_datasets(self):
        datasets = Datasets()

        dataset_id = datasets.create_dataset()
        self.assertIsNotNone(dataset_id)

        dataset = datasets.get_dataset(dataset_id)
        self.assertIsNotNone(dataset)

    def test_indices(self):
        for_document = 'document1'
        indices = ByDocumentIndices()

        index_id = indices.create_index(for_document)
        self.assertIsNotNone(index_id)

        index = indices.get_index(index_id)
        self.assertIsNotNone(index)
