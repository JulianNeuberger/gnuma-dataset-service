# Dataset Service for the GNUMA project

## Installation

### Run via docker

#### Requirements

1. PostgreSQL 13, available [here](https://www.postgresql.org/download/)
2. Docker 20, available [here](https://docs.docker.com/get-docker/)

#### Setup

1. Clone this repository and navigate into it
2. open a psql command line (https://www.postgresql.org/docs/13/app-psql.html)
3. Setup a PostgreSQL user named e.g. `ai4eventsourcing` with password `ai4eventsourcing` ([see instructions](https://www.postgresql.org/docs/8.0/sql-createuser.html))
4. Setup a database e.g. named `ai4eventsourcing` (see [here](https://www.postgresql.org/docs/9.0/sql-createdatabase.html))
5. Grant permissions to the user created in step 3 to database created in step 4, run `GRANT ALL PRIVILEGES ON DATABASE ai4eventsourcing to ai4eventsourcing;`
6. Get the ip of your machine (`ipconfig /all` on Win, `ifconfig -a` on Unix) and note it down
7. Set the environment variable `POSTGRES_HOST` to the ip from step 6
8. Start the project by running `docker compose up` in the projects root folder 
   (still in the same command line from step 7)

### Manual setup

#### Requirements

1. PostgreSQL 13, available [here](https://www.postgresql.org/download/)
2. conda 4.9, e.g. the Miniconda [installation](https://conda.io/miniconda.html) 

#### Setup

1. Clone this repository
2. open a psql command line (https://www.postgresql.org/docs/13/app-psql.html)
3. Setup a PostgreSQL user named e.g. `ai4eventsourcing` with password `ai4eventsourcing` ([see instructions](https://www.postgresql.org/docs/8.0/sql-createuser.html))
4. Setup a database e.g. named `ai4eventsourcing` (see [here](https://www.postgresql.org/docs/9.0/sql-createdatabase.html))
5. Grant permissions to the user created in step 3 to database created in step 4, run `GRANT ALL PRIVILEGES ON DATABASE ai4eventsourcing to ai4eventsourcing;`
6. Setup the conda virtual environment via `conda env create -f env.yml`
7. Activate the installed environment via `conda activate ai4-document-service`
9. Run the server via `python server.py` in the root directory of your project

## Usage

The `./documentation/` folder contains api documentation (`gnuma.postman_collection.json`) 
as [Postman](https://www.postman.com/) collection, which you can 
[import](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/).

Alternatively you can use the `gnuma.openapi_3.json` file with SwaggerUI,
e.g. via [this tool](https://github.com/flasgger/flasgger).

Both document the usage for creating, listing, deleting and viewing datasets.
 
