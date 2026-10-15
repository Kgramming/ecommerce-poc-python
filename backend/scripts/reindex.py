#!/usr/bin/env python3
"""Rebuild the Elasticsearch `orders` index from Postgres in one step.

Useful after experimenting with sync strategies, or any time the dashboard
looks stale:  python backend/scripts/reindex.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from esync import reindex_es  # noqa: E402

if __name__ == "__main__":
    n = reindex_es()
    print(f"reindexed {n} orders into Elasticsearch")
