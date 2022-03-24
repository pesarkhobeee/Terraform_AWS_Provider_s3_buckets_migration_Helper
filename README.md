# Terraform AWS Provider s3 buckets migration Helper
Sadly [version 4](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/guides/version-4-upgrade) of the AWS Provider introduced lots of breaking changes for [aws_s3_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/guides/version-4-upgrade#s3-bucket-refactor) without providing any smooth way for people to migrate their buckets.

In this situation, we can try to have an automatic way to detect buckets that have arguments and attributes which become read-only and comment on their related resources with the right names!
This will speed up the migration and reduce the possibility of human mistakes while copy-pasting the names and attributes in high numbers. 

### How to use

After cloning this repo please follow the below steps inside its directory:

```
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Then you can see what it can do by running `python main.py --help`:

```
usage: main.py [-h] [-d] [--log-level LOG_LEVEL] terraform_files [terraform_files ...]

positional arguments:
  terraform_files       search pattern file, if `-` pattern is read from stdin

optional arguments:
  -h, --help            show this help message and exit
  -d, --dry-run         not adding any comments to the terraform files
  --log-level LOG_LEVEL
                        set the logging level. Defaults to WARNING.
```

As you can see, you can feed it directly by your s3 buckets name or using some better ways like the combination with [ag](https://github.com/ggreer/the_silver_searcher):

```
ag -l 'resource \"aws_s3_bucket\"' ~/works/terraform/**/*.tf |  python main.py - --dry-run
```

Don't forget to adjust `templates` based on your needs and hope this tiny helper ease a bit your migration pain :)
