from youtube_transcript_api import YouTubeTranscriptApi
from smart_text_formatter import SmartTextFormatter
import copy
import yaml

video_id = 'GNSedMOH9bg'

transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

transcript = transcript_list.find_transcript(['en'])

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

translation_list = create_translation_structure('en', transcript.fetch(), transcript.translate('pl').fetch())

print(yaml.dump(translation_list, allow_unicode=True, sort_keys=False))

