from youtube_transcript_api import YouTubeTranscriptApi
import copy
import yaml
import argparse
import logging
from pathlib import Path
from youtube import get_yt_id

MAIN_LANGUAGE='pl'


parser = argparse.ArgumentParser(description='Download transcript data for definition file')
parser.add_argument('--definition', '-d', type=argparse.FileType('r'), required=True)
parser.add_argument('--output', '-o', type=str, required=True)


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
