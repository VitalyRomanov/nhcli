import sys
from pprint import pprint

from nhcli import ArgumentConfigParser

args = ArgumentConfigParser()
# adding to DEFAULT group
# must specify default value
args.add_argument("--optional_DEFAULT", default=None, help="Optional argument for default group")
# must specify default value
args.add_argument("positional_DEFAULT", default=None, help="Positional argument for default group")

group = args.add_argument_group("GROUP1", description="This group is used for ...")
# adding to GROUP1
# can specify type
group.add_argument("--optional1_GROUP1", default=0., type=float, help="Optional argument for GROUP1")
# can specify destination variable
group.add_argument("--optional2_GROUP1", "-o2g1", dest="optional_value", default=0, type=int, help="Optional argument for GROUP1 with short option")

group = args.add_argument_group("GROUP2", description="This group is used for ...")
# can specify destination variable
group.add_argument("positional_GROUP2", default=None, type=str, help="Positional argument for GROUP2")

# parse command line options
# default values will be replaced with values from command line
# any changes made before `parse`, for example with `update_config`, will be overwritten
args.parse()


# can call with --help option
# usage: example.py [-h] [--config CONFIG] [--optional_DEFAULT OPTIONAL_DEFAULT]
#                   [--optional1_GROUP1 OPTIONAL1_GROUP1]
#                   [--optional2_GROUP1 OPTIONAL_VALUE]
#                   positional_DEFAULT positional_GROUP2
#
# positional arguments:
#   positional_DEFAULT    Positional argument for default group
#   positional_GROUP2     Positional argument for GROUP2
#
# optional arguments:
#   -h, --help            show this help message and exit
#   --config CONFIG       Path to config file. All command line options will be
#                         overriden with config file content.
#   --optional_DEFAULT OPTIONAL_DEFAULT
#                         Optional argument for default group
#   --optional1_GROUP1 OPTIONAL1_GROUP1
#                         Optional argument for GROUP1
#   --optional2_GROUP1 OPTIONAL_VALUE, -o2g1 OPTIONAL_VALUE
#                         Optional argument for GROUP1 with short option


# `get_default_config` can be called before `parse`
default_config = args.get_default_config()
pprint(default_config, indent=4)
# {   'DEFAULT': {   'optional1_GROUP1': 0.0,
#                    'optional_DEFAULT': None,
#                    'optional_value': 0,
#                    'positional_DEFAULT': None,
#                    'positional_GROUP2': 'None'}}


# if `get_config` called before `parse`, then default config is returned
parsed_config = args.get_config()
pprint(parsed_config, indent=4)
# {   'DEFAULT': {   'optional1_GROUP1': 1.0,
#                    'optional_DEFAULT': 'some',
#                    'optional_value': 1,
#                    'positional_DEFAULT': 'positional_default',
#                    'positional_GROUP2': 'positional_group2'}}


# Can perform partial update using `update_config`
args.update_config(optional_value=1)
updated_config = args.get_config()
pprint(updated_config, indent=4)
# {   'DEFAULT': {   'optional1_GROUP1': 1.0,
#                    'optional_DEFAULT': 'some',
#                    'optional_value': 1,
#                    'positional_DEFAULT': 'positional_default',
#                    'positional_GROUP2': 'positional_group2'}}


args.save_config("config.yaml")
args.load_config("config.yaml")
loaded_config = args.get_config()
pprint(loaded_config, indent=4)
# {   'DEFAULT': {   'optional1_GROUP1': 1.0,
#                    'optional_DEFAULT': 'some',
#                    'optional_value': 1,
#                    'positional_DEFAULT': 'positional_default',
#                    'positional_GROUP2': 'positional_group2'}}


# specify --config path/to/config to load existing config
sys.argv = ["", "--config", "config.yaml"]
args.parse()
loaded_from_file = args.get_config()
pprint(loaded_config)
# {'DEFAULT': {'optional1_GROUP1': 1.0,
#              'optional_DEFAULT': 'some',
#              'optional_value': 1,
#              'positional_DEFAULT': 'positional_default',
#              'positional_GROUP2': 'positional_group2'}}


