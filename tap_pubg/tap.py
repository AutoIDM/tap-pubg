"""pubg tap class."""

from typing import List 

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_pubg.streams import (
    PlayersStream,
    PlayerMatches,
    TelemetryStream,
)
# TODO: Compile a list of custom stream types here
#       OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [
    PlayersStream,
    PlayerMatches,
    TelemetryStream,
]


class Tappubg(Tap):
    """pubg tap class."""
    name = "tap-pubg"

    # TODO: Update this section with the actual config values you expect:
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
            description="Player Names you'd like to pull"
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
