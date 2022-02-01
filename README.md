# Dataset Service for the GNUMA project

## Installation

### Requirements

1. PostgreSQL 13, available [here](https://www.postgresql.org/download/)
4. conda 4.9, e.g. the Miniconda [installation](https://conda.io/miniconda.html) 

### Setup

1. Clone this repository
2. open a psql command line (https://www.postgresql.org/docs/13/app-psql.html)
3. Setup a PostgreSQL user named e.g. `ai4eventsourcing` with password `ai4eventsourcing` ([see instructions](https://www.postgresql.org/docs/8.0/sql-createuser.html))
4. Setup a database e.g. named `ai4eventsourcing` (see [here](https://www.postgresql.org/docs/9.0/sql-createdatabase.html))
5. Grant permissions to the user created in step 3 to database created in step 4, run `GRANT ALL PRIVILEGES ON DATABASE ai4eventsourcing to ai4eventsourcing;`
6. Setup the conda virtual environment via `conda env create -f env.yml`
7. Activate the installed environment via `conda activate ai4-document-service`
9. Run the server via `python server.py` in the root directory of your project