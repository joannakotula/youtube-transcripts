from youtube_transcript_api import YouTubeTranscriptApi
from smart_text_formatter import SmartTextFormatter

video_id = 'GNSedMOH9bg'

transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

transcript = transcript_list.find_transcript(['en'])

formatter = SmartTextFormatter()

print(formatter.format_transcript(transcript.fetch()))
print('-------------')
print(formatter.format_transcript(transcript.translate('pl').fetch()))

