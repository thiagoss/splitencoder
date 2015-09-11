import argparse

from splitencoder.splitter import split

parser = argparse.ArgumentParser()
parser.add_argument('-cd', '--chunks-dir',
                    help='Directory that contains the video chunks')
parser.add_argument('-i', '--input', help='Input video')
args = vars(parser.parse_args())

split(args['input'], args['chunks_dir'])
