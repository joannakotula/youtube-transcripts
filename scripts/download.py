from youtube_transcript_api import YouTubeTranscriptApi
import copy
import yaml
import argparse
import logging
from pathlib import Path
from youtube import get_yt_id

MAIN_LANGUAGE='pl'
PARAGRAPH_BREAK_DURATION = 1.0


parser = argparse.ArgumentParser(description='Download transcript data for definition file')
parser.add_argument('--definition', '-d', type=argparse.FileType('r'), required=True)
parser.add_argument('--output', '-o', type=str, required=True)
parser.add_argument('--force', '-f', default=False, action='store_true')


def prepare_entries(lang, transcript):
    new_trans = copy.deepcopy(transcript)
    offset = 0.0
    for item in new_trans:
        item['lang'] = lang
        item['text'] = item['text'].strip().replace('\n', ' ')
        if offset > 0 and item['start'] - offset >= PARAGRAPH_BREAK_DURATION:
            item['new_paragraph'] = True
        offset = item['start'] + item['duration']
    return new_trans
    

def create_translation_structure(orig_lang, original_transcript, pl_transcript):
    ret = prepare_entries(orig_lang, original_transcript) + prepare_entries('pl', pl_transcript)
    ret.sort(key = lambda elem: elem['start'])
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

if Path(args.output).exists() and not args.force:
    logging.warning(f"File {args.output} already exists, skipping")
    exit()

definition = yaml.safe_load(args.definition)
transcripts_data = prepare_transcripts(definition['url'], definition['original_language'])

with open(args.output, 'w') as f:
    f.write(yaml.dump(transcripts_data, allow_unicode=True, sort_keys=False))
