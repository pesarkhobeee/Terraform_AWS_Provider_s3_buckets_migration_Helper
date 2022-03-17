#!/usr/bin/env python3

import sys
import hcl2
import logging
import argparse
from jinja2 import Environment, FileSystemLoader

most_wanted = {"acl", "lifecycle_rule", "logging", "website", "policy"}
suspects    = {}


def investigator(file_name, dry_run):
  with open(file_name, 'r') as file:
    hcl_dict = hcl2.load(file)
    s3_buckets = [x for x in hcl_dict["resource"] if "aws_s3_bucket" in x]
    for s3_bucket in s3_buckets:
      s3_bucket_name = next(iter( s3_bucket["aws_s3_bucket"]))
      for e in most_wanted.intersection(s3_bucket["aws_s3_bucket"][s3_bucket_name]):
        suspects.setdefault(file_name, {})
        suspects[file_name].setdefault(s3_bucket_name, [])
        suspects[file_name][s3_bucket_name].append(e)
        logging.info(s3_bucket)
        if not dry_run:
            commentor(file_name, s3_bucket_name, e)

def reporter():
    print(f"It is going to change {len(suspects)} files, you can find the details here:")
    print(suspects)

def commentor(file_name, s3_bucket_name, wanted_element):
  logging.info(f"{file_name}, {s3_bucket_name}, {wanted_element}")
  env = Environment(
    loader = FileSystemLoader('./templates'),
    trim_blocks=True,
    lstrip_blocks=True)
  template = env.get_template(wanted_element + ".jinja2")
  new_comment = template.render(bucket_name=s3_bucket_name)
  logging.info(new_content)
  with open(file_name, "a") as file_object:
    file_object.write(new_comment)

def main(args):
  try:
    for f in args.terraform_files:
        logging.info(f"Investigating {f.name}")
        investigator(f.name, args.dry_run)
    print("finished")
    reporter()
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
