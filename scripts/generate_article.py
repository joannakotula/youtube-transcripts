import argparse
import sys
import yaml
from transcript import Transcript

PARAGRAPH_BREAK_DURATION = 1.0

parser = argparse.ArgumentParser(description='Generate jekyll page with transcripts')
parser.add_argument('--definition', '-d', type=argparse.FileType('r'), required=True)
parser.add_argument('--transcript', '-t', type=argparse.FileType('r'), required=True)
parser.add_argument('--output', '-o', type=argparse.FileType('w'), default=sys.stdout)


def writeln(file, line):
    file.write(f"{line}\n")
    

def get_text_paragraphs_by_time(transcript):
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


args = parser.parse_args()

definition = yaml.safe_load(args.definition)
transcript_data = yaml.safe_load(args.transcript)
transcript_pl = Transcript('pl', transcript_data)
transcript_en = Transcript('en', transcript_data)


writeln(args.output, "--")
writeln(args.output, f"tags: {definition['tags']}")
writeln(args.output, "--")

writeln(args.output, f"# {definition['title']}")
writeln(args.output, f"Tytuł oryginalny: {definition['original_title']}")
writeln(args.output, "")
writeln(args.output, f"## Transkrypt po polsku")
writeln(args.output, "")
writeln(args.output, '\n\n'.join(get_text_paragraphs_by_time(transcript_pl)))
writeln(args.output, "")
writeln(args.output, f"## Transkrypt po angielsku")
writeln(args.output, "")
writeln(args.output, '\n\n'.join(get_text_paragraphs_by_time(transcript_en)))