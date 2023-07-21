#!/usr/bin/env python
# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

"""Script that downloads a public dataset and streams it to an Elasticsearch cluster"""

import csv
from os.path import abspath, join, dirname, exists
import tqdm
import urllib3
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from dotenv import load_dotenv
import os


load_dotenv()

ES_CID = os.getenv('ES_CID')
ES_USER = os.getenv('ES_USER')
ES_PWD = os.getenv('ES_PWD')

RENNES_TRAFFIC = (
    "https://data.rennesmetropole.fr/explore/dataset/etat-du-trafic-en-temps-reel/download?format=csv&timezone=Europe/Berlin&use_labels_for_header=false"
)
DATASET_PATH = join(dirname(abspath(__file__)), "rennes-traffic.csv")
CHUNK_SIZE = 16384


def download_dataset():
    """Downloads the public dataset if not locally downlaoded
    and returns the number of rows are in the .csv file.
    """
    if not exists(DATASET_PATH):
        http = urllib3.PoolManager()
        resp = http.request("GET", RENNES_TRAFFIC, preload_content=False)

        if resp.status != 200:
            raise RuntimeError("Could not download dataset")

        with open(DATASET_PATH, mode="wb") as f:
            chunk = resp.read(CHUNK_SIZE)
            while chunk:
                f.write(chunk)
                chunk = resp.read(CHUNK_SIZE)

    with open(DATASET_PATH) as f:
        return sum([1 for _ in f]) - 1




def generate_actions():
    """Reads the file through csv.DictReader() and for each row
    yields a single document. This function is passed into the bulk()
    helper to create many documents in sequence.
    """
    with open(DATASET_PATH, mode="r") as f:
        reader = csv.DictReader(f,delimiter=";")

        for row in reader:
            time = row["datetime"].split("+")
            doc = {
                "_op_type": "create",
                "@timestamp": row["datetime"],
                "trafficstatus": row["trafficstatus"],
                "locationreference": row["predefinedlocationreference"],
                "denomination": row["denomination"],
                "hierarchie": row["hierarchie"],
                "hierarchie_dv": row["hierarchie_dv"],
                "insee": row["insee"],
                "vehicles": row["vehicleprobemeasurement"],
                "traveltime.reliability": row["traveltimereliability"],
                "traveltime.duration": row["traveltime"],
                "maxspeed": row["vitesse_maxi"],
                "averagevehiclespeed": row["averagevehiclespeed"],
            }


            coords = row["geo_point_2d"]
            coordslist = coords.split(",",1)
            lat = coordslist[0]
            lon = coordslist[1]
            if lat not in ("", "0") and lon not in ("", "0"):
                doc["location"] = {"lat": float(lat), "lon": float(lon)}
            yield doc

def main():
    print("Loading dataset...")
    number_of_docs = download_dataset()

    client = Elasticsearch(
        # Add your cluster configuration here!
        cloud_id=ES_CID,
        basic_auth=(ES_USER, ES_PWD)
    )
    print(client.info)
    print("Creating an index...")
    # create_index(client)

    print("Indexing documents...")
    progress = tqdm.tqdm(unit="docs", total=number_of_docs)
    successes = 0

    for ok, action in streaming_bulk(
            client=client, index="metrics-rennes_traffic-default", actions=generate_actions(),
    ):
        progress.update(1)
        successes += ok
    print("Indexed %d/%d documents" % (successes, number_of_docs))


if __name__ == "__main__":
    main()