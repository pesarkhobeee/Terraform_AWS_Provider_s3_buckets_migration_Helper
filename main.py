#!/usr/bin/env python3

import sys
import hcl2
import logging
import argparse
from jinja2 import Environment, FileSystemLoader

most_wanted = {"acl", "lifecycle_rule", "logging", "website", "policy", "server_side_encryption_configuratio"}
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
    print(f"It found {len(suspects)} files, you can find the details here:")
    print(suspects)

def commentor(file_name, s3_bucket_name, wanted_element):
  logging.info(f"{file_name}, {s3_bucket_name}, {wanted_element}")
  env = Environment(
    loader = FileSystemLoader('./templates'),
    trim_blocks=True,
    lstrip_blocks=True)
  template = env.get_template(wanted_element + ".jinja2")
  new_comment = template.render(bucket_name=s3_bucket_name)
  logging.info(new_comment)
  with open(file_name, "a") as file_object:
    file_object.write(new_comment)

def input_lines(inp: str):
    """Get lines from input."""
    if inp == ['-']:
        return sys.stdin

    return inp

def main(args):
  try:
    for f in input_lines(args.terraform_files):
        file_name  = f.rstrip()
        # ignore empty lines and comments
        if len(file_name) == 0:
            continue
        logging.info(f"Investigating {file_name}")
        investigator(file_name, args.dry_run)
    reporter()
  except Exception as e:
    logging.critical("Fatal error hapend: {}".format(e))
    sys.exit(1)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'terraform_files', nargs='+', default=[],
      help='search pattern file, if `-` pattern is read from stdin'
  )
  parser.add_argument('-d', '--dry-run', action='store_true',
          help='not adding any comments to the terraform files')
  parser.add_argument(
      '--log-level', type=str, default="WARNING",
      help='set the logging level. Defaults to WARNING.'
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
