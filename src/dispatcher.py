import json

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from interface.service import DatasetsService


class MessageDispatcher:
    def __init__(self, datasets_service: DatasetsService):
        print(f'Building AMQP message dispatcher, using dataset service with id {hex(id(datasets_service))}....')
        self._datasets_service = datasets_service

    def dispatch(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        print(f'Got AMQP message with routing key {method.routing_key}.')
        # TODO: use factory for building and handling different messages based on routing key
        if method.routing_key == 'document.event.deleted':
            body = body.decode('utf-8')
            body = json.loads(body)
            document_id = body['id']
            self._datasets_service.remove_documents_from_all_datasets([document_id])
        # TODO: should we always acknowledge the message, even if it was not handled properly?
        channel.basic_ack(delivery_tag=method.delivery_tag)
