"""pubg tap class."""

from typing import List 

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_pubg.streams import (
    PlayersStream,
    PlayerMatches,
    MatchesStream,
#    TelemetryStream,
)
STREAM_TYPES = [
    PlayersStream,
    PlayerMatches,
    MatchesStream,
#    TelemetryStream,
]


class Tappubg(Tap):
    """pubg tap class."""
    name = "tap-pubg"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "player_names",
            th.ArrayType(th.StringType),
            required=True,
            description="Player Names sepearted by commas that you'd like to pull, maximum of 10"
        ),
        th.Property(
            "platform",
            th.StringType,
            required=True,
            description="platform, ie steam"
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
