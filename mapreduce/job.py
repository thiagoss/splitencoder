import os
import uuid

from mrjob.job import MRJob


class SplitencoderJob(MRJob):

    def configure_options(self):
        super(SplitencoderJob, self).configure_options()
        self.add_passthrough_option(
            '--files-root', type='str', default='.',
            help='Path where all files are located')

    def load_options(self, args):
        super(SplitencoderJob, self).load_options(args)
        self.files_root = self.options.files_root

    def _fetch_file(self, filename):
        with open(os.path.join(self.files_root, filename), 'r') as f:
            return f.read()

    def _transcode(self, chunk):
        return ''.join(str(ord(ch)) for ch in chunk)

    def _transfer_transcoded_file(self, transcoded_chunk):
        filename = uuid.uuid4().hex
        with open(os.path.join(self.files_root, filename), 'w') as t_file:
            t_file.write(transcoded_chunk)
        return filename

    def mapper(self, _, filename):
        key, chunk = tuple(self._fetch_file(filename).split())
        transcoded_chunk = self._transcode(chunk)
        transcoded_filename = self._transfer_transcoded_file(transcoded_chunk)
        yield key, transcoded_filename

    def reducer(self, key, values):
        yield key, '\n'.join([self._fetch_file(f) for f in values])


if __name__ == '__main__':
    SplitencoderJob.run()
