import argparse
from dataclasses import replace
import translators as ts
import re
import yaml
from datetime import datetime
import os
from pytube import YouTube, Playlist

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description='Generate defintions for youtube url')
parser.add_argument('--url', '-u', type=str, required=True)
parser.add_argument('--lang', '-l', type=str, default='en')
parser.add_argument('--out', '-o', type=str, default=f"{SCRIPT_PATH}/../data/definitions")
parser.add_argument('--category', '-c', type=str)
parser.add_argument('--tag', '-t', action='append', default=[])

SPACES_PATTERN = re.compile(r'[\s\_\-\.\?,:;\'\"\)\(\&]+')
MAIN_LANGUAGE = 'pl'
MAX_FILENAME_LENGTH = 45

def file_name_from_title(title):
    return re.sub(SPACES_PATTERN, "_", title.lower())

def format_upload_date(upload_date):
    return upload_date.strftime("%Y-%m-%d")

def get_filename(definition):
    datepart = format_upload_date(definition['upload_date'])
    title = re.sub(r'[^\x00-\x7f]',r'', definition['original_title'])
    name = file_name_from_title(f"{datepart} {title}")
    if len(name) > MAX_FILENAME_LENGTH:
        index = name.find('_', MAX_FILENAME_LENGTH)
        return name[:index]
    return name

def build_definition(movie):
    return {
        "id": movie.video_id,
        "url": movie.watch_url,
        "original_title": movie.title,
        "title": ts.google(movie.title , to_language = MAIN_LANGUAGE),
        "original_description": movie.description.replace("\n", ""),
        "original_tags": movie.keywords,
        "upload_date": movie.publish_date,
        "author": movie.author,
        'original_language': args.lang,
        'category': args.category,
        'tags': args.tag + [movie.author]
    }


def dump_yaml(value):
    return yaml.dump(value, allow_unicode=True, sort_keys=False)

args = parser.parse_args()
print(args)

video_links = Playlist(args.url).video_urls

for link in video_links:
    print(f"Preparing data for: {link}")
    movie = YouTube(link)
    if args.lang in movie.captions or MAIN_LANGUAGE in movie.captions:
        print(f"Creating definition for: {movie.title}")
        definition = build_definition(movie)
        filename = get_filename(definition)
        out_path = f"{args.out}/{filename}.yaml"
        with open(out_path, 'w') as f:
            f.write(dump_yaml(definition))
    else:
        print(f"No subtitles for {args.lang} in {movie.title} - skipping")
        print(list(movie.captions.keys()))
