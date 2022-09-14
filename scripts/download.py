from youtube_transcript_api import YouTubeTranscriptApi
import copy
import yaml
import argparse
from urllib.parse import urlparse, parse_qs
import logging
from pathlib import Path

MAIN_LANGUAGE='pl'


parser = argparse.ArgumentParser(description='Download transcript data for definition file')
parser.add_argument('--definition', '-d', type=argparse.FileType('r'), required=True)
parser.add_argument('--output', '-o', type=str, required=True)

# method based on: https://stackoverflow.com/a/54383711
def get_yt_id(url):
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)
    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[1]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]
   # returns None for invalid YouTube url


def create_translation_structure(orig_lang, original_transcript, pl_transcript):
    ret = copy.deepcopy(original_transcript)
    for i, orig in enumerate(ret):
        pl = pl_transcript[i]
        orig_text = orig['text']
        pl_text = pl['text']
        orig['text'] = {
            orig_lang: orig_text.strip().replace('\n', ' '),
            'pl': pl_text.strip().replace('\n', ' ')
        }
    return {
        'status': 'generated',
        'content': ret
    }

def prepare_transcripts(url, original_language):
    video_id = get_yt_id(url)
    if not video_id:
        logging.error(f"Invalid url: {url}")
        exit(123)

    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    transcript = transcript_list.find_transcript([original_language])
    # TODO: what if original_language = MAIN_LANGUAGE?
    return create_translation_structure(original_language, transcript.fetch(), transcript.translate(MAIN_LANGUAGE).fetch())
    

args = parser.parse_args()

if Path(args.output).exists():
    logging.warning(f"File {args.output} already exists, skipping")
    exit()

definition = yaml.safe_load(args.definition)
transcripts_data = prepare_transcripts(definition['url'], definition['original_language'])

with open(args.output, 'w') as f:
    f.write(yaml.dump(transcripts_data, allow_unicode=True, sort_keys=False))
