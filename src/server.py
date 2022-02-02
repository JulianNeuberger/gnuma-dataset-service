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
    config = configparser.ConfigParser()
    root_folder = Path(os.path.abspath(__file__)).parent.parent
    config_location = f'{root_folder}{os.path.sep}config.ini'
    if not os.path.exists(config_location):
        logwrapper.error(f'No config file at {config_location}. Make sure to copy config.ini.template to config.ini '
                         f'and adjust it according to your environment.')
        raise ValueError(f'No config file found at {config_location}')
    logwrapper.warning(f'Reading configuration from {config_location}')
    config.read(config_location)

    # event sourcing configuration
    os.environ["INFRASTRUCTURE_FACTORY"] = "eventsourcing.postgres:Factory"
    os.environ["POSTGRES_DBNAME"] = config['postgresql']['database']
    os.environ["POSTGRES_HOST"] = config['postgresql']['host']
    os.environ["POSTGRES_PORT"] = config['postgresql']['port']
    os.environ["POSTGRES_USER"] = config['postgresql']['user']
    os.environ["POSTGRES_PASSWORD"] = config['postgresql']['pass']
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

    listener = AMQPListener(
        host=config['rabbitmq']['host'],
        port=int(config['rabbitmq']['port']),
        username=config['rabbitmq']['user'],
        password=config['rabbitmq']['pass'],
        on_message=dispatcher.dispatch
    )
    listener.start()

    app.run(debug=True, use_reloader=False, host='0.0.0.0')

    listener.stop()
    listener.join()
    datasets_service.shutdown()
