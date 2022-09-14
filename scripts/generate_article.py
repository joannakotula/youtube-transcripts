import argparse
from enum import Enum
import sys
import yaml
from transcript import Transcript

PARAGRAPH_BREAK_DURATION = 1.0

parser = argparse.ArgumentParser(description='Generate jekyll page with transcripts')
parser.add_argument('--definition', '-d', type=argparse.FileType('r'), required=True)
parser.add_argument('--transcript', '-t', type=argparse.FileType('r'), required=True)
parser.add_argument('--output', '-o', type=argparse.FileType('w'), default=sys.stdout)


class TranscriptStatus(Enum):
    generated   = "Wygenerowany automatycznie"
    in_progress = "W trakcie redakcji"
    done        = "Zredagowany"


class ArticleData:
    def __init__(self, definition_data, transcripts_data):
        self.definition_data = definition_data
        self.transcripts_data = transcripts_data

    def status(self):
        return TranscriptStatus[self.transcripts_data['status']].value

    def tags(self):
        return self.definition_data['tags'] + [self.status()]

    def title(self):
        return definition['title']
    
    def original_title(self):
        return definition['original_title']

    def content(self, language):
        transcript = Transcript(language, self.transcripts_data)
        return '\n\n'.join(self.get_text_paragraphs_by_time(transcript))
    

    def get_text_paragraphs_by_time(self, transcript):
        paragraphs = []
        offset = 0.0
        last_paragraph = None
        for line in transcript:
            if last_paragraph and line.start - offset < PARAGRAPH_BREAK_DURATION:
                last_paragraph += ' ' + line.text
            else:
                if last_paragraph:
                    paragraphs.append(last_paragraph)
                last_paragraph = line.text
            offset = line.start + line.duration
        return paragraphs

def writeln(file, line):
    file.write(f"{line}\n")

args = parser.parse_args()

definition = yaml.safe_load(args.definition)
transcript_data = yaml.safe_load(args.transcript)

article = ArticleData(definition, transcript_data)


writeln(args.output, "--")
writeln(args.output, f"tags: {article.tags()}")
writeln(args.output, "--")

writeln(args.output, f"# {article.title()}")
writeln(args.output, f"Tytuł oryginalny: {article.original_title()}")
writeln(args.output, "")
writeln(args.output, f"## Transkrypt po polsku")
writeln(args.output, "")
writeln(args.output, article.content('pl'))
writeln(args.output, "")
writeln(args.output, f"## Transkrypt po angielsku")
writeln(args.output, "")
writeln(args.output, article.content('en'))
