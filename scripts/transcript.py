class TranscriptLine:
    def __init__(self, text, start, duration):
        self.text = text
        self.start = start
        self.duration = duration

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

    def line(self, index):
        full_line = self.data['content'][index]
        return TranscriptLine(full_line['text'][self.language], full_line['start'], full_line['duration'])

    def size(self):
        return len(self.data['content'])

    def status(self):
        return self.data['status']

    def __iter__(self):
        return TranscriptIterator(self)    