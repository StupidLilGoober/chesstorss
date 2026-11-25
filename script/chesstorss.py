import json
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime

# loading configurations

try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
except FileNotFoundError:
    print("You need a `config.json` file.")
    sys.exit(1)

# optional configuration

optional = config.get("optional", {})

email = optional.get("email") or ""
json_output = optional.get("jsonOutput") or None
rss_output = optional.get("rssOutput") or "output/chess.rss"

# API setup

URL = "https://api.chess.com/pub/player"
LIST_OF_GAMES_URL = f"{URL}/{config['player']}/games/archives"

print(LIST_OF_GAMES_URL)

user_agent_header = f"ChessToRSS/1.0 ({email})"
print(f"The User-Agent header used will be `{user_agent_header}`")

# get games

request = urllib.request.Request(
    LIST_OF_GAMES_URL,
    headers={"User-Agent": user_agent_header}
)

try:
    with urllib.request.urlopen(request, timeout=5) as response:
        list_of_games = json.load(response)
except urllib.error.HTTPError as error:
    print(f"{LIST_OF_GAMES_URL} returned a {error.code}: {error.reason}.")
    sys.exit(1)

games = []

for url in list_of_games["archives"]:
    print(f"Processing month: {url}")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": user_agent_header}
    )

    with urllib.request.urlopen(request, timeout=5) as response:
        games.append(json.load(response)["games"])

# optional JSON output

if json_output:
    path = Path(json_output)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(games, file, indent=2, ensure_ascii=False)

# create the XML for the RSS

def get_pgn_date(pgn: str):
    for line in pgn.splitlines():
        line = line.strip()

        if line.startswith("[Date"):
            return line.removeprefix('[Date "').removesuffix('"]')

    return "UNKNOWN"


def get_rss_date(pgn: str):
    date = get_pgn_date(pgn)

    if date == "UNKNOWN":
        return None

    try:
        parsed = datetime.strptime(date, "%Y.%m.%d")
    except ValueError:
        return None

    parsed = parsed.replace(tzinfo=timezone.utc)

    return format_datetime(parsed)


def convert_post(post: dict):
    rss_post = ET.Element("item")

    rss_post_title = ET.SubElement(rss_post, "title")
    rss_post_title.text = (
        f"{post['white']['username']} vs {post['black']['username']}"
    )

    rss_post_link = ET.SubElement(rss_post, "link")
    rss_post_link.text = post["url"]

    rss_post_guid = ET.SubElement(rss_post, "guid")
    rss_post_guid.text = post["url"]

    rss_post_description = ET.SubElement(rss_post, "description")
    rss_post_description.text = f"White: {post['white']['result']}, Black: {post['black']['result']}"

    pgn = post.get("pgn")

    if not pgn:
        print(f"Game missing PGN: {post.get('url', 'Unknown URL')}")
        return rss_post

    pub_date = get_rss_date(pgn)

    if pub_date:
        rss_post_pub_date = ET.SubElement(rss_post, "pubDate")
        rss_post_pub_date.text = pub_date

    return rss_post


def create_feed():
    rss_feed = ET.Element("rss", {"version": "2.0"})
    rss_feed_channel = ET.SubElement(rss_feed, "channel")

    rss_feed_title = ET.SubElement(rss_feed_channel, "title")
    rss_feed_title.text = f"Chess RSS - {config['player']}"

    rss_feed_description = ET.SubElement(rss_feed_channel, "description")
    rss_feed_description.text = f"Games played by {config['player']}"

    rss_feed_link = ET.SubElement(rss_feed_channel, "link")
    rss_feed_link.text = f"https://chess.com/member/{config['player']}"

    return rss_feed, rss_feed_channel


rss_feed, rss_feed_channel = create_feed()

for month in games:
    for game in month:
        rss_feed_channel.append(convert_post(game))

tree = ET.ElementTree(rss_feed)
ET.indent(tree, space="  ")

path = Path(rss_output)
path.parent.mkdir(parents=True, exist_ok=True)

tree.write(path, encoding="utf-8", xml_declaration=True)
