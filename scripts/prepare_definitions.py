import argparse
import translators as ts
import re
import yaml
from datetime import datetime
import os
from pytube import YouTube, Playlist

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser(description='Generate defintions for youtube url')
parser.add_argument('--url', '-u', type=str, required=True)
parser.add_argument('--names', '-n', type=argparse.FileType('r+'), default=f"{SCRIPT_PATH}/../data/videos.yaml")
parser.add_argument('--lang', '-l', type=str, default='en')
parser.add_argument('--out', '-o', type=str, default=f"{SCRIPT_PATH}/../data/definitions")
parser.add_argument('--category', '-c', type=str)
parser.add_argument('--tag', '-t', action='append')

SPACES_PATTERN = re.compile(r'[\s-]+')
SPECIAL_CHARACTERS = "ąćęłńóśżź"
REPLACE_CHARACTERS = "acelnoszz"
MAIN_LANGUAGE = 'pl'

def file_name_from_title(title):
    filename_base = re.sub(SPACES_PATTERN, "_", title.lower())
    trans_table = filename_base.maketrans(SPECIAL_CHARACTERS, REPLACE_CHARACTERS)
    return filename_base.translate(trans_table)

def get_filename(names, definition):
    video_id = definition['id']
    if video_id in names:
        return names[video_id]
    name = file_name_from_title(definition['title'])
    names[video_id] = name
    return name

    
def format_upload_date(upload_date):
    date = datetime.strptime(upload_date, "%Y%m%d")
    return date.strftime("%Y-%m-%d")

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

names = yaml.safe_load(args.names)

video_links = Playlist(args.url).video_urls

for link in video_links:
    print(f"Preparing data for: {link}")
    movie = YouTube(link)
    if args.lang in movie.captions:
        print(f"Creating definition for: {movie.title}")
        definition = build_definition(movie)
        filename = get_filename(names, definition)
        out_path = f"{args.out}/{filename}.yaml"
        with open(out_path, 'w') as f:
            f.write(dump_yaml(definition))
    else:
        print(f"No subtitles for {args.lang} in {movie.title} - skipping")

args.names.seek(0)
args.names.write(dump_yaml(names))
args.names.truncate()
