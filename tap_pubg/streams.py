"""Stream type classes for tap-pubg."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable
from singer_sdk import typing as th  # JSON Schema typing helpers
from singer.schema import Schema

import json
import requests

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


class PlayerMatches(PubgStream):
    name = "player_matches"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "match.json"
    records_jsonpath = "$.data[0].relationships.matches.data[*]"

    @property
    def path(self):
        path = "/players?filter[playerNames]="+",".join(self.config["player_names"])
        return path

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "match_id": record["id"],
        }



class MatchesStream(PubgStream):
    "Matches data"
    name = "matches" 
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "matches.json"
    path = "/matches/{match_id}"

    parent_stream_type = PlayerMatches

    #What if we want other child streams here beyond telemtry? 
    #I think we'd just expand this to include them, and all the relevent child streams would use only the data they needed

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        included = record["included"] #List of Dicts
        teletermy_includes = list(filter(lambda included: included["type"]=="asset" and included["attributes"]["name"]=="telemetry", included))
        if (len(teletermy_includes) != 1):
            self.logger.error(f"Record JSON data for failure: {json.dumps(record)}")
            raise Exception("Matches includes more than one telemtry record, I'm dead")
        return {
            "URL": teletermy_includes[0]["attributes"]["URL"],
        }

class TelemetryStream(PubgStream):
    "Telemetry Data"

    name = "match_telemetry" 
    primary_keys = ["MatchId"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "telemetry.json"
    path = ""

    parent_stream_type = MatchesStream
    def get_url(self, context: Optional[dict]):
        """Return the API URL root, configurable via tap settings."""
        return context["URL"]

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield {"data": response.json()}
