

import sys
import argparse
import pkg_resources
import traceback;

from air_anchor_tracker.watcher import Watcher
from air_anchor_tracker.data import MongoRepo

from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging
from sawtooth_sdk.processor.log import log_configuration
from sawtooth_sdk.processor.config import get_log_config
from sawtooth_sdk.processor.config import get_log_dir


DISTRIBUTION_NAME = 'sawtooth-locationKey'


def parse_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '--zmq-url',
        default='tcp://localhost:4004',
        help='Endpoint for the zqm connection')
    
    parser.add_argument(
        '--mongo-url',
        default='mongodb://localhost:27017',
        help='Endpoint for the mongo connection'
    )
    
    parser.add_argument(
        '--mongo-database',
        default='AirAnchorDocuments',
        help='Name of the mongo database document'
    )
    
    parser.add_argument(
        '--mongo-collection',
        default='Coords',
        help='Name of the mongodb collection where events data are safe'
    )

    return parser.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    processor = None
    try:
        
        mongoRepo = MongoRepo(mongo_url=opts.mongo_url, 
                      mongo_database=opts.mongo_database, mongo_collection=opts.mongo_collection)
        
        Watcher(opts.zmq_url, mongoRepo).start()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:  # pylint: disable=broad-except
        print("Error: {}".format(e), file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    finally:
        if processor is not None:
            processor.stop()
