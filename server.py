import os

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from dispatcher import MessageDispatcher
from interface.service import DatasetsService
from messages.listener import AMQPListener
from resources import Dataset, DatasetList, DebugDocumentRemover

if __name__ == '__main__':
    # event sourcing configuration
    os.environ["INFRASTRUCTURE_FACTORY"] = "eventsourcing.postgres:Factory"
    os.environ["POSTGRES_DBNAME"] = "ai4eventsourcing"
    os.environ["POSTGRES_HOST"] = "127.0.0.1"
    os.environ["POSTGRES_PORT"] = "5433"
    os.environ["POSTGRES_USER"] = "ai4eventsourcing"
    os.environ["POSTGRES_PASSWORD"] = "ai4eventsourcing"
    os.environ["POSTGRES_CONN_MAX_AGE"] = "10"
    os.environ["POSTGRES_PRE_PING"] = "y"
    os.environ["POSTGRES_LOCK_TIMEOUT"] = "5"
    os.environ["POSTGRES_IDLE_IN_TRANSACTION_SESSION_TIMEOUT"] = "5"

    app = Flask(__name__)
    cors = CORS(app, resources={
        r'/api/*': {
            'origins': '*'
        }
    })
    api = Api(app, prefix='/api/v1/')

    datasets_service = DatasetsService()
    dispatcher = MessageDispatcher(datasets_service)

    api.add_resource(Dataset, '/datasets/<dataset_id>', resource_class_kwargs={'datasets_service': datasets_service})
    api.add_resource(DatasetList, '/datasets', resource_class_kwargs={'datasets_service': datasets_service})

    # FIXME: get credentials from config file
    listener = AMQPListener('h2826957.stratoserver.net', 5672, 'rabbitmqtest', 'rabbitmqtest', dispatcher.dispatch)
    listener.start()

    app.run(debug=True, use_reloader=False)

    listener.stop()
    listener.join()
    datasets_service.shutdown()
