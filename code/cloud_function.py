"""Google Cloud Functions for Chicago weather scrapping."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from google.cloud import pubsub_v1


def publish_to_pubsub(
    project_id: str,
    topic_id: str,
    data_pth: str,
) -> None:
    # initialize publisher client
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    try:
        df = pd.read_csv(data_pth)
        publisher.publish(
            topic_path, df.to_json(orient="records").encode("utf-8")
        )
    except Exception as e:
        raise RuntimeError(f"Failed to publish to Pub/Sub: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-pth", type=str, required=True)
    parser.add_argument("--project-id", type=str, required=True)
    parser.add_argument("--topic-id", type=str, required=True)
    args = parser.parse_args()

    assert Path(args.data_pth).exists()

    publish_to_pubsub(
        project_id=args.project_id,
        topic_id=args.topic_id,
        data_pth=str(Path(args.data_pth).resolve()),
    )
