

import sys
import argparse
import traceback;

from air_anchor_tracker.watcher import Watcher
from air_anchor_tracker.data import MongoRepo


DISTRIBUTION_NAME = 'sawtooth-locationKey'

def parse_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '--zmq-url',
        default='tcp://localhost:4004',
        help='Endpoint for the zqm connection')
        
    parser.add_argument(
        '--rabbitmq',
        default='localhost',
        help='url of the rabbitmq broker connection'
    )


    return parser.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    processor = None
    try:
                
        Watcher(opts.zmq_url, opts.rabbitmq).start()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:  # pylint: disable=broad-except
        print("Error: {}".format(e), file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    finally:
        if processor is not None:
            processor.stop()
