from unittest import TestCase
from uuid import uuid4

from domain.dataset import Dataset
from domain.index import ByDocumentIndex


class TestDatasetAggregate(TestCase):
    def test_dataset_can_be_managed(self):
        dataset = Dataset.create()
        self.assertEqual(dataset.version, 1)
        self.assertEqual(dataset.contained_documents, [])

        dataset.add_document('1')
        self.assertEqual(dataset.version, 2)
        self.assertEqual(dataset.contained_documents, ['1'])

        dataset.add_document('2')
        self.assertEqual(dataset.version, 3)
        self.assertEqual(dataset.contained_documents, ['1', '2'])

        dataset.remove_document('1')
        self.assertEqual(dataset.version, 4)
        self.assertEqual(dataset.contained_documents, ['2'])

        dataset.remove_document('3')
        self.assertEqual(dataset.version, 5)
        self.assertEqual(dataset.contained_documents, ['2'])

    def test_index_can_be_updated(self):
        for_document = 'document1'

        index = ByDocumentIndex.create(for_document)
        self.assertEqual(index.version, 1)
        self.assertEqual(index.datasets, [])

        # add document to index, used in dataset 'dataset1'
        dataset_1_id = uuid4()
        index.add_dataset_to_index(dataset_1_id)
        self.assertEqual(index.version, 2)
        self.assertEqual(index.datasets, [dataset_1_id])

        dataset_2_id = uuid4()
        index.add_dataset_to_index(dataset_2_id)
        self.assertEqual(index.version, 3)
        self.assertEqual(index.datasets, [dataset_1_id, dataset_2_id])

        index.remove_dataset_from_index(dataset_1_id)
        self.assertEqual(index.version, 4)
        self.assertEqual(index.datasets, [dataset_2_id])

        index.remove_dataset_from_index(uuid4())
        self.assertEqual(index.version, 5)
        self.assertEqual(index.datasets, [dataset_2_id])

        irrelevant_index = ByDocumentIndex.create('document2')
        # make sure creating another index doesn't affect this one
        self.assertEqual(index.version, 5)
        self.assertEqual(index.datasets, [dataset_2_id])
