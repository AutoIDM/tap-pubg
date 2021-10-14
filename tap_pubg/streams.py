"""Stream type classes for tap-pubg."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable
import requests
from singer_sdk import typing as th  # JSON Schema typing helpers
from singer.schema import Schema

from singer_sdk.plugin_base import PluginBase as TapBaseClass
from tap_pubg.client import PubgStream
# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
# TODO: - Override `UsersStream` and `GroupsStream` with your own stream definition.
#       - Copy-paste as many times as needed to create multiple stream types.

class PlayersStream(PubgStream):
    """Define custom stream."""
    name = "player"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "player.json"

    @property
    def path(self):
        path = "/players?filter[playerNames]="+",".join(self.config["player_names"])
        return path
