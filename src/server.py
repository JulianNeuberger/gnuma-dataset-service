import configparser
import os
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from api.resources import Dataset, DatasetList
from dispatcher import MessageDispatcher
from interface.service import DatasetsService
from messages.listener import AMQPListener
from util import logwrapper

if __name__ == '__main__':
    # event sourcing configuration
    os.environ["INFRASTRUCTURE_FACTORY"] = "eventsourcing.postgres:Factory"
    os.environ["POSTGRES_DBNAME"] = os.environ["GNUMA_DB_NAME"]
    os.environ["POSTGRES_HOST"] = os.environ["GNUMA_DB_HOST"]
    os.environ["POSTGRES_PORT"] = os.environ["GNUMA_DB_PORT"]
    os.environ["POSTGRES_USER"] = os.environ["GNUMA_DB_USER"]
    os.environ["POSTGRES_PASSWORD"] = os.environ["GNUMA_DB_PASS"]
    os.environ["POSTGRES_CONN_MAX_AGE"] = "10"
    os.environ["POSTGRES_PRE_PING"] = "y"
    os.environ["POSTGRES_LOCK_TIMEOUT"] = "5"
    os.environ["POSTGRES_IDLE_IN_TRANSACTION_SESSION_TIMEOUT"] = "5"

    logwrapper.info(f'Will connect to database {os.environ["POSTGRES_DBNAME"]} '
                    f'at postgres://{os.environ["POSTGRES_HOST"]}:{os.environ["POSTGRES_PORT"]}')

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

    listener = AMQPListener(
        host=os.environ["RABBITMQ_HOST"],
        port=int(os.environ["RABBITMQ_PORT"]),
        username=os.environ["RABBITMQ_USER"],
        password=os.environ["RABBITMQ_PASS"],
        on_message=dispatcher.dispatch
    )
    listener.start()

    app.run(debug=True, use_reloader=False, host='0.0.0.0')

    listener.stop()
    listener.join()
    datasets_service.shutdown()
