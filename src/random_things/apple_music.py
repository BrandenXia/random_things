import plistlib
from argparse import FileType
from io import TextIOWrapper
from typing import cast

import pandas as pd
import rich

from random_things.utils import cli


@cli
def apple_music_stats(lib: FileType("r") = "Library.xml"):
    """Analyzes Apple Music data from Library.xml file"""
    lib = cast(TextIOWrapper, lib)
    p: dict = plistlib.load(lib.buffer)

    data = preprocess(p)
    stats = StatsReports(data)
    for title, report in stats.scan_methods():
        title = title.replace("_", " ").capitalize()
        rich.print(f"[bold]{title}:[/]")
        rich.print(report(stats))
        print()


def preprocess(data: dict) -> pd.DataFrame:
    """Preprocess the data from the plist file."""
    assert "Tracks" in data, "Tracks not found in the file"
    assert isinstance(data["Tracks"], dict), "Tracks is not a dictionary"

    df = pd.DataFrame(data["Tracks"].values())

    # set index
    df.set_index("Track ID", inplace=True)

    # drop unused
    df.drop(
        [
            "Album Artist",
            "Size",
            "Disc Number",
            "Bit Rate",
            "Kind",
            "Sample Rate",
            "Play Date UTC",
            "Normalization",
            "Artwork Count",
            "Persistent ID",
            "Track Type",
            "File Folder Count",
            "Library Folder Count",
            "Sort Album",
            "Sort Name",
            "Comments",
            "Composer",
            "Track Count",
            "Disc Count",
            "Location",
            "Track Number",
            "Date Modified",
            "Date Added",
            "Play Date",
            "Skip Date",
        ],
        axis=1,
        inplace=True,
    )

    # rename and set correct types
    df.rename(columns={"Total Time": "Duration"}, inplace=True)
    df["Duration"] = pd.to_timedelta(df["Duration"], unit="ms")
    df["Play Count"] = df["Play Count"].astype("Int64")
    df["Skip Count"] = df["Skip Count"].astype("Int64")
    df["Year"] = df["Year"].astype("Int64")

    # fill missing values
    df.loc[df["Play Count"].isnull(), "Play Count"] = 0
    df.loc[df["Skip Count"].isnull(), "Skip Count"] = 0

    return df


class StatsReports:
    def __init__(self, data: pd.DataFrame) -> None:
        self.df = data

    @classmethod
    def scan_methods(cls):
        methods = [
            (n, m)
            for n in dir(cls)
            if (m := getattr(cls, n)) and callable(m) and n in cls.__dict__
        ]
        return filter(
            lambda x: x[0] != "scan_methods" and not x[0].startswith("__"), methods
        )

    def most_played_tracks(self) -> str:
        most_played = self.df.sort_values("Play Count", ascending=False).head(3)[
            ["Name", "Artist", "Play Count"]
        ]
        return "\n".join(
            [
                "[blue italic]%s[/] by [bold green]%s[/] - [bold red]%d[/] plays"
                % tuple(item)
                for _, item in most_played.iterrows()
            ]
        )

    def most_skipped_tracks(self) -> str:
        most_skipped = self.df.sort_values("Skip Count", ascending=False).head(3)[
            ["Name", "Artist", "Skip Count"]
        ]
        return "\n".join(
            [
                "[blue italic]%s[/] by [bold green]%s[/] - [bold red]%d[/] skips"
                % tuple(item)
                for _, item in most_skipped.iterrows()
            ]
        )

    def most_played_artists(self) -> str:
        most_played = (
            self.df.groupby("Artist")[["Play Count"]]
            .sum()
            .sort_values("Play Count", ascending=False)
            .head(3)
        )[["Play Count"]].reset_index()
        return "\n".join(
            [
                "[bold green]%s[/] - [bold red]%d[/] plays" % tuple(item)
                for _, item in most_played.iterrows()
            ]
        )

    def most_played_albums(self) -> str:
        most_played = (
            self.df.groupby("Album")[["Play Count"]]
            .sum()
            .sort_values("Play Count", ascending=False)
            .head(3)
        )[["Play Count"]].reset_index()
        return "\n".join(
            [
                "[bold cyan]%s[/] - [bold red]%d[/] plays" % tuple(item)
                for _, item in most_played.iterrows()
            ]
        )

    def most_played_genres(self) -> str:
        most_played = (
            self.df.groupby("Genre")[["Play Count"]]
            .sum()
            .sort_values("Play Count", ascending=False)
            .head(3)
        )[["Play Count"]].reset_index()
        return "\n".join(
            [
                "[bold green]%s[/] - [bold red]%d[/] plays" % tuple(item)
                for _, item in most_played.iterrows()
            ]
        )

    def top_three_genres(self) -> str:
        top_three = self.df["Genre"].value_counts().head(3)
        return "\n".join(
            [
                "[bold yellow]%s[/] - [bold red]%d[/] songs" % (genre, count)
                for genre, count in top_three.items()
            ]
        )

    def top_three_artists(self) -> str:
        top_three = self.df["Artist"].value_counts().head(3)
        return "\n".join(
            [
                "[bold green]%s[/] - [bold red]%d[/] songs" % (artist, count)
                for artist, count in top_three.items()
            ]
        )

    def total_time(self) -> str:
        # total_time = self.df["Duration"] * self.df["Play Count"] # BUG: AssertionError
        total_time = pd.Timedelta(0)
        for _, row in self.df.iterrows():
            total_time += row["Duration"] * row["Play Count"]
        return f"Total time: {total_time}"

    def total_play_count(self) -> str:
        return f"Total play count: {self.df['Play Count'].sum()}"


if __name__ == "__main__":
    apple_music_stats()
