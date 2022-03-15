#!/usr/bin/env python3

import argparse
import hcl2
import logging
import sys

most_wanted = {"acl", "lifecycle_rule", "logging", "website", "policy"}

def investigator(file_name, dry_run):
  with open(file_name, 'r') as file:
      hcl_dict = hcl2.load(file)
      s3_buckets = [x for x in hcl_dict["resource"] if "aws_s3_bucket" in x]
      for s3_bucket in s3_buckets:
        s3_bucket_name = next(iter( s3_bucket["aws_s3_bucket"]))
        for e in most_wanted.intersection(s3_bucket["aws_s3_bucket"][s3_bucket_name]):
            print(f"Element `{e}` was found in `{s3_bucket_name}` bucket inside the `{file_name}`, Do something.")
            logging.info(s3_bucket)
            if not dry_run:
                commentor(file_name, s3_bucket_name, e)

def commentor(file_name, s3_bucket_name, wanted_element):
  print(file_name, s3_bucket_name, wanted_element)

def main(args):
    try:
        for f in args.terraform_files:
            logging.info(f"Investigating {f.name}")
            investigator(f.name, args.dry_run)
    except Exception as e:
        logging.critical("Fatal error hapend: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'terraform_files', nargs='+', default=[], type=argparse.FileType('r'),
        help='List of terraform files that we would like to investigate about'
    )
    parser.add_argument('-d', '--dry-run', action='store_true',
            help='Not adding any comments to the terraform files')
    parser.add_argument(
        '--log-level', type=str, default="WARNING",
        help='Set the logging level. Defaults to WARNING.'
    )
    parsed_args = parser.parse_args()
    logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=parsed_args.log_level,
        datefmt='%Y-%m-%dT%H:%M:%S%z')
    logging.info(
        f"Starting with given arguments: {format(parsed_args)}"
    )
    main(parsed_args)
