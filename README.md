# Dataset Service for the GNUMA project

## Installation

### Run via docker

#### Requirements

1. Docker 20, available [here](https://docs.docker.com/get-docker/)

#### Setup

1. Clone this repository and navigate into it
2. Copy the `.env.template` file to `.env` and at least set the password 
   for the `RABBITMQ_PASS` variable (found in slides),
   adjust other parameters to your liking.  
3. Start the project by running `docker compose up` in the projects root folder 
   (still in the same command line from step 7)

## Usage

The `./documentation/` folder contains api documentation (`gnuma.postman_collection.json`) 
as [Postman](https://www.postman.com/) collection, which you can 
[import](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/).

Alternatively you can use the `gnuma.openapi_3.json` file with SwaggerUI,
e.g. via [this tool](https://github.com/flasgger/flasgger).

Both document the usage for creating, listing, deleting and viewing datasets.
 
