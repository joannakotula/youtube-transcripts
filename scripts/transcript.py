class TranscriptLine:
    def __init__(self, text, new_paragraph):
        self.text = text
        self.new_paragraph = new_paragraph

class TranscriptIterator:
    def __init__(self, transcript):
        self.transcript = transcript
        self.index = 0;

    def __next__(self):
        if self.index < self.transcript.size():
            line = self.transcript.line(self.index)
            self.index+=1
            return line
        else:
            raise StopIteration

class Transcript(object):
    def __init__(self, language, data):
        self.language = language
        self.data = data
        self.lines = list(filter(lambda entry: entry['lang'] == language, data['content']))

    def line(self, index):
        full_line = self.lines[index]
        return TranscriptLine(full_line['text'], 'new_paragraph' in full_line and full_line['new_paragraph'])

    def size(self):
        return len(self.lines)

    def status(self):
        return self.data['status']

    def __iter__(self):
        return TranscriptIterator(self)    