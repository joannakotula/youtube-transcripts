from youtube_transcript_api.formatters import Formatter

PARAGRAPH_BREAK_DURATION = 1.0

class TranscriptEntry():
    def __init__(self, raw_entry):
        self.text = raw_entry['text'].strip().replace('\n', ' ')
        self.start = raw_entry['start']
        self.end = self.start + raw_entry['duration']

class FormattedTranscriptBuilder():
    def __init__(self) -> None:
        self.lines = []
        self.last_line = ''
        self.offset = 0.0

    def add_entry(self, raw_entry):
        entry = TranscriptEntry(raw_entry)
        if self.last_line and entry.start - self.offset < PARAGRAPH_BREAK_DURATION:
            self.last_line += ' ' + entry.text
        else:
            if self.last_line:
                self.lines.append(self.last_line)
            self.last_line = entry.text
        self.offset = entry.end

    def __str__(self) -> str:
        return '\n\n'.join(self.lines)
        

class SmartTextFormatter(Formatter):
    def format_transcript(self, transcript, **kwargs):
        builder = FormattedTranscriptBuilder()
        for entry in transcript:
            builder.add_entry(entry)
        return builder

    def format_transcripts(self, transcripts, **kwargs):
        # Do your custom work in here to format a list of transcripts, but return a string.
        return 'your processed output data as a string.'