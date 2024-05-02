import plistlib
from math import floor

import pandas as pd


def format_timedelta(value, time_format="{days} days, {hours2}:{minutes2}:{seconds2}"):
    """Format a timedelta object as a string."""
    # https://stackoverflow.com/a/30339105
    if hasattr(value, "seconds"):
        seconds = value.seconds + value.days * 24 * 3600
    else:
        seconds = int(value)

    seconds_total = seconds

    minutes = int(floor(seconds / 60))
    minutes_total = minutes
    seconds -= minutes * 60

    hours = int(floor(minutes / 60))
    hours_total = hours
    minutes -= hours * 60

    days = int(floor(hours / 24))
    days_total = days
    hours -= days * 24

    years = int(floor(days / 365))
    years_total = years
    days -= years * 365

    return time_format.format(
        **{
            "seconds": seconds,
            "seconds2": str(seconds).zfill(2),
            "minutes": minutes,
            "minutes2": str(minutes).zfill(2),
            "hours": hours,
            "hours2": str(hours).zfill(2),
            "days": days,
            "years": years,
            "seconds_total": seconds_total,
            "minutes_total": minutes_total,
            "hours_total": hours_total,
            "days_total": days_total,
            "years_total": years_total,
        }
    )


# load the data
with open("../../Library/Application Support/JetBrains/PyCharm2023.3/scratches/Library.xml", "rb") as f:
    data = plistlib.load(f)
    print(data)
df = pd.DataFrame(data["Tracks"].values())
df.set_index("Track ID", inplace=True)
df.rename(columns={"Total Time": "Duration"}, inplace=True)
df["Duration"] = pd.to_timedelta(df["Duration"], unit="ms")
df["Track Number"] = df["Track Number"].astype("Int64")
df["Year"] = df["Year"].astype("Int64")
df["Date Modified"] = pd.to_datetime(df["Date Modified"])
df["Date Added"] = pd.to_datetime(df["Date Added"])
df["Play Count"] = df["Play Count"].astype("Int64")
df["Play Date"] = pd.to_datetime(df["Play Date UTC"])
df["Skip Count"] = df["Skip Count"].astype("Int64")
df["Skip Date"] = pd.to_datetime(df["Skip Date"])

del data

# delete unnecessary columns
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
    ],
    axis=1,
    inplace=True,
)

# fill missing values
df.loc[df["Play Count"].isnull(), "Play Count"] = 0
df.loc[df["Skip Count"].isnull(), "Skip Count"] = 0

# most played tracks, artists, albums, genres
most_played_tracks = df.sort_values("Play Count", ascending=False).head(3)[
    ["Name", "Artist", "Album", "Play Count"]
]
most_skipped_tracks = df.sort_values("Skip Count", ascending=False).head(3)[
    ["Name", "Artist", "Album", "Skip Count"]
]
most_played_artists = (
    df.groupby("Artist")[["Play Count"]]
    .sum()
    .sort_values("Play Count", ascending=False)
    .head(3)
)
most_played_albums = (
    df.groupby("Album")[["Play Count"]]
    .sum()
    .sort_values("Play Count", ascending=False)
    .head(3)
)
most_played_genres = (
    df.groupby("Genre")[["Play Count"]]
    .sum()
    .sort_values("Play Count", ascending=False)
    .head(3)
)

# top three genres and artists
top_three_genres = df["Genre"].value_counts().head(3)
top_three_artists = df["Artist"].value_counts().head(3)

# total play time
# https://github.com/pandas-dev/pandas/issues/58054
# BUG: AssertionError when multiplying timedelta Series with a pandas nullable dtype Series
# Unable to directly multiply and sum, loop through the rows instead
# TODO: wait for the fix
total_time = pd.Timedelta(0)
for _, row in df.iterrows():
    total_time += row["Duration"] * row["Play Count"]

# total play count
total_play_count = df["Play Count"].sum()

# report
print("Most played tracks:")
for _, row in most_played_tracks.iterrows():
    print(
        f"- {row['Name']} by {row['Artist']} from {row['Album']} ({row['Play Count']} plays)"
    )

print("\nMost skipped tracks:")
for _, row in most_skipped_tracks.iterrows():
    print(
        f"- {row['Name']} by {row['Artist']} from {row['Album']} ({row['Skip Count']} skips)"
    )

print("\nMost played artists:")
for artist, play_count in most_played_artists.iterrows():
    print(f"- {artist} ({play_count['Play Count']} plays)")

print("\nMost played albums:")
for album, play_count in most_played_albums.iterrows():
    print(f"- {album} ({play_count['Play Count']} plays)")

print("\nMost played genres:")
for genre, play_count in most_played_genres.iterrows():
    print(f"- {genre} ({play_count['Play Count']} plays)")

print("\nTop three genres:")
for genre, count in top_three_genres.items():
    print(f"- {genre} ({count} songs)")

print("\nTop three artists:")
for artist, count in top_three_artists.items():
    print(f"- {artist} ({count} songs)")

print(
    f"\nTotal play time: {format_timedelta(total_time, time_format='{days} days, {hours} hours, {minutes} minutes')}"
)
print(f"Total play count: {total_play_count}")
