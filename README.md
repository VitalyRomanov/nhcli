![](https://github.com/VitalyRomanov/nhcli/actions/workflows/run-tests.yaml/badge.svg)

# NHCLI

Simple argument parser with groups that can be saved in config file. Key features:
- All arguments are assigned to a group. Different groups are easy to pass to different functions as **kwargs.
- Arguments can be saved to and loaded from yaml file.
- Interface for specifying arguments is the same as in `argpase` with slight differences, e.g. default value should always be specified.
- After adding argument with `add_argument`, a default configuration file can be produced.
- Arguments can be updated during execution by calling `update_config`
- Configuration file can be loaded from command line interface by specifying `--config` option.

## Installation

```bash
pip install git+https://github.com/VitalyRomanov/nhcli
```

## Quick Start

Class `ArgumentConfigParser` allows specifying command line options and at the same time generating default configuration specification. All arguments are assigned to a group. Argument names should not repeat between different groups. Group names cannot repeat. If no group specified, arguments are added to the `DEFAULT` group.

```python
from nhcli import ArgumentConfigParser

args = ArgumentConfigParser()
# adding to DEFAULT group
# must specify default value
args.add_argument("--optional_DEFAULT", default=None, help="Optional argument for default group")
# must specify default value
args.add_argument("positional_DEFAULT", default=None, help="Positional argument for default group")

group = args.add_argument_group("GROUP1")
# adding to GROUP1
# can specify type
group.add_argument("--optional1_GROUP1", default=0., type=float, help="Optional argument for GROUP1")
# can specify destination variable
group.add_argument("--optional2_GROUP1", "-o2g1", dest="optional_value", default=0, type=int, help="Optional argument for GROUP1 with short option")

group = args.add_argument_group("GROUP2")
# can specify destination variable
group.add_argument("positional_GROUP2", default=None, type=str, help="Positional argument for GROUP2")

# parse command line options
# default values will be replaced with values from command line
# any changes made before `parse`, for example with `update_config`, will be overwritten
args.parse()
```

Specifying `--help` from command line will produce a help message
```text
usage: example.py [-h] [--config CONFIG] [--optional_DEFAULT OPTIONAL_DEFAULT]
                  [--optional1_GROUP1 OPTIONAL1_GROUP1]
                  [--optional2_GROUP1 OPTIONAL_VALUE]
                  positional_DEFAULT positional_GROUP2

positional arguments:
  positional_DEFAULT    Positional argument for default group

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Path to config file. All command line options will be
                        overriden with config file content.
  --optional_DEFAULT OPTIONAL_DEFAULT
                        Optional argument for default group

GROUP1:
  This group is used for ...

  --optional1_GROUP1 OPTIONAL1_GROUP1
                        Optional argument for GROUP1
  --optional2_GROUP1 OPTIONAL_VALUE, -o2g1 OPTIONAL_VALUE
                        Optional argument for GROUP1 with short option

GROUP2:
  This group is used for ...

  positional_GROUP2     Positional argument for GROUP2
```

`get_default_config` can be called before `parse`
```python
default_config = args.get_default_config()
# {   'DEFAULT': {   'optional1_GROUP1': 0.0,
#                    'optional_DEFAULT': None,
#                    'optional_value': 0,
#                    'positional_DEFAULT': None,
#                    'positional_GROUP2': 'None'}}
```

If `get_config` called before `parse`, then default config is returned
```python
parsed_config = args.get_config()
# {   'DEFAULT': {   'optional1_GROUP1': 1.0,
#                    'optional_DEFAULT': 'some',
#                    'optional_value': 1,
#                    'positional_DEFAULT': 'positional_default',
#                    'positional_GROUP2': 'positional_group2'}}
```

Can perform partial update using `update_config`
```python
args.update_config(optional_value=1)
updated_config = args.get_config()
# {   'DEFAULT': {   'optional1_GROUP1': 1.0,
#                    'optional_DEFAULT': 'some',
#                    'optional_value': 1,
#                    'positional_DEFAULT': 'positional_default',
#                    'positional_GROUP2': 'positional_group2'}}
```

Saving and loading 
```python
args.save_config("config.yaml")
args.load_config("config.yaml")
loaded_config = args.get_config()
# {   'DEFAULT': {   'optional1_GROUP1': 1.0,
#                    'optional_DEFAULT': 'some',
#                    'optional_value': 1,
#                    'positional_DEFAULT': 'positional_default',
#                    'positional_GROUP2': 'positional_group2'}}
```

Can specify `--config path/to/config` to load existing config
```python
# sys.argv = ["", "--config", "config.yaml"]
args.parse()
loaded_from_file = args.get_config()
# {'DEFAULT': {'optional1_GROUP1': 1.0,
#              'optional_DEFAULT': 'some',
#              'optional_value': 1,
#              'positional_DEFAULT': 'positional_default',
#              'positional_GROUP2': 'positional_group2'}}
```

Reset config
```python
args.reset_config()
```

## TODO
- [ ] Implement groups as subconfigs. This way can save parts of configs separately, for example just saving config for a model
- [ ] Create subconfig slices to pass several groups. Can create configs that share some groups.
- [ ] Work with config object instead of dictionaries. Right now the transition from config to dict is irreversible.

