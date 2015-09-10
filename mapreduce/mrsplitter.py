import argparse
import uuid
import os

parser = argparse.ArgumentParser()
parser.add_argument('-fr', '--files-root', help='Path where the file')
parser.add_argument('-fn', '--file-name', help='Name of the file to read')
args = vars(parser.parse_args())

with open(os.path.join(args['files_root'],
          args['file_name']), 'r') as input_file:
    for line in input_file:
        filename = uuid.uuid4().hex
        with open(os.path.join(args['files_root'],
                  filename), 'w') as output_file:
            output_file.write('%s %s' % (args['file_name'], line))
        print filename
