import os
import shutil
import sys

from mrjob.job import MRJob
from splitencoder.transcoder import transcode
from splitencoder.merger import merge


class SplitencoderJob(MRJob):

    def configure_options(self):
        super(SplitencoderJob, self).configure_options()
        self.add_passthrough_option(
            '--files-root', type='str', default='.',
            help='Path where all files are located')

    def load_options(self, args):
        super(SplitencoderJob, self).load_options(args)
        self.files_root = self.options.files_root
        self.output_file = sys.argv[-1]
        self.output_extension = os.path.splitext(self.output_file)[1]

    def _get_key(self, filename):
        return os.path.split(filename)[0]

    def _transcode(self, chunk):
        transcoded_file = '%s%s' % (os.path.splitext(chunk)[0],
                                    self.output_extension)
        path = os.path.split(chunk)[0]
        tmp_file = os.path.join(path, 'tmp')
        os.rename(chunk, tmp_file)
        transcode(tmp_file, transcoded_file)
        os.remove(tmp_file)
        return transcoded_file

    def mapper(self, _, filename):
        key = self._get_key(filename)
        transcoded_chunk = self._transcode(filename)
        yield key, transcoded_chunk

    def reducer(self, key, values):
        transcoded_chunk = next(values)
        path = os.path.split(transcoded_chunk)[0]
        merge_pattern = '%s/*' % path
        merge(merge_pattern, self.output_file)
        shutil.rmtree(path, ignore_errors=True)
        yield key, '\n'.join(values)


if __name__ == '__main__':
    SplitencoderJob.run()
