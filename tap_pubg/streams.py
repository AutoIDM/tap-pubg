"""Stream type classes for tap-pubg."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable
from singer_sdk import typing as th  # JSON Schema typing helpers
from singer.schema import Schema

import json
import requests

from singer_sdk.plugin_base import PluginBase as TapBaseClass
from tap_pubg.client import PubgStream
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

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
    """Need seperate records for each match a player has. Note that this is only the last 14 days of Matches"""
    name = "player_match"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "player_matches.json"
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
    name = "match" 
    primary_keys = ["id"]
    replication_key = "createdAt"
    schema_filepath = SCHEMAS_DIR / "match.json"
    path = "/matches/{match_id}"

    parent_stream_type = PlayerMatches

    def post_process(self, row: dict, context: Optional[dict]) -> dict:
        """As needed, append or transform raw data to match expected structure."""
        included = row["included"] #List of Dicts
        teletermy_includes = list(filter(lambda included: included["type"]=="asset" and included["attributes"]["name"]=="telemetry", included))
        if (len(teletermy_includes) != 1):
            self.logger.warning(f"Record did not contain telemetry info, skipping. Record data: {json.dumps(record)}")
			#TODO test to see if running this while a match is going will fail due to there not being a telemetry record
            return None
        telemetry_data = {
            "URL": teletermy_includes[0]["attributes"]["URL"],
			#Used this isntead of match attributes as it's possible we query a match while it's happening. If we don't have telemetry data we don't want to mark this as complete
            "createdAt": teletermy_includes[0]["attributes"]["createdAt"],
        }
        row.update(telemetry_data)
        return row

    #What if we want other child streams here beyond telemtry? 
    #I think we'd just expand this to include them, and all the relevent child streams would use only the data they needed
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        self.logger.info(f"record: {record}")
        return {
            "URL": record["URL"],
        }


class TelemetryStream(PubgStream):
    "Telemetry Data"

    name = "match_telemetry" 
    primary_keys = ["URL"]
    #TODO if parent stream is called will this always be called? 
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "telemetry.json"
    path = ""
    parent_stream_type = MatchesStream
    
    def get_url(self, context: Optional[dict]):
        """Return the API URL root, configurable via tap settings."""
        self.logger.info(f"context in get_url: {context}")
        return context["URL"]

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield {"data": response.json()}
