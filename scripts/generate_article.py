import argparse
from enum import Enum
import os
import sys
import time
import yaml
from transcript import Transcript
from youtube import get_yt_id

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
        return self.definition_data.get('tags', []) + [self.status()]

    def title(self):
        return self.definition_data['title']

    def category(self):
        return self.definition_data['category']

    def upload_date(self):
        return self.definition_data['upload_date']

    def created_date(self):
        return self.definition_data['created_date']
    
    def original_title(self):
        return self.definition_data['original_title']

    def video_url(self):
        return self.definition_data['url']

    def video_id(self):
        return get_yt_id(self.video_url())

    def cover(self):
        video_id = self.video_id()
        return f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"

    def content(self, language):
        transcript = Transcript(language, self.transcripts_data)
        return '\n\n'.join(self.get_text_paragraphs(transcript))
    
    def get_text_paragraphs(self, transcript):
        paragraphs = []
        last_paragraph = None
        for line in transcript:
            if last_paragraph:
                if line.new_paragraph:
                    paragraphs.append(last_paragraph)
                    last_paragraph = line.text
                else:
                    last_paragraph += ' ' + line.text
            else:
                last_paragraph = line.text
        return paragraphs

def writeln(file, line):
    file.write(f"{line}\n")

def get_last_modified_timestamp(filename):
    time_float = os.path.getmtime(filename)
    return time.ctime(time_float)

def get_last_modified(definition_file, transcript_file):
    definition_timestamp = get_last_modified_timestamp(definition_file.name)
    transcript_timestamp = get_last_modified_timestamp(transcript_file.name)
    max_modified_timestamp = max(definition_timestamp, transcript_timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(max_modified_timestamp))

args = parser.parse_args()

definition = yaml.safe_load(args.definition)
transcript_data = yaml.safe_load(args.transcript)

article = ArticleData(definition, transcript_data)


writeln(args.output, "---")
writeln(args.output, f"tags: {article.tags()}")
writeln(args.output, f"title: {article.title()}")
writeln(args.output, f"cover: {article.cover()}")
writeln(args.output, f"category: {article.category()}")
writeln(args.output, f"upload_date: {article.upload_date()}")
writeln(args.output, f"created_date: {article.created_date()}")
writeln(args.output, f"modify_date: {get_last_modified(args.definition, args.transcript)}")
writeln(args.output, "sidebar:")
writeln(args.output, "  nav: transcripts-en")
writeln(args.output, "---")

writeln(args.output, f"Tytuł oryginalny: {article.original_title()}")
writeln(args.output, "")
writeln(args.output, f"Data publikacji wideo: {article.upload_date().strftime('%Y-%m-%d')}")
writeln(args.output, "")
writeln(args.output, "## Wideo")
writeln(args.output, f"{{% include youtube.html id=\"{article.video_id()}\" %}}")
writeln(args.output, "")
writeln(args.output, f"## Transkrypt po polsku")
writeln(args.output, "")
writeln(args.output, article.content('pl'))
writeln(args.output, "")
writeln(args.output, f"## Transkrypt po angielsku")
writeln(args.output, "")
writeln(args.output, article.content('en'))
