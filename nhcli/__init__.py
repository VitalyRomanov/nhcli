import sys
from argparse import ArgumentParser
from copy import deepcopy

import yaml


class ArgumentConfigError(Exception):
    def __init__(self, *args):
        super(ArgumentConfigError, self).__init__(*args)


def load_config(path):
    return yaml.load(open(path, "r").read(), Loader=yaml.Loader)


def save_config(config, path):
    yaml.dump(config, open(path, "w"))


def _parse_arg_name(arg_name):
    positional_name = long = short = None
    if arg_name.startswith("--"):
        long = arg_name.strip("--")
    elif arg_name.startswith("-"):
        short = arg_name.strip("-")
    else:
        positional_name = arg_name
    return positional_name, long, short


def figure_out_name(*args, **kwargs):
    target_name = None
    if "dest" in kwargs:
        target_name = kwargs["dest"]
    else:
        if len(args) == 0:
            raise ArgumentConfigError("provide positional arguments or set `dest` argument")
        elif len(args) == 1:  # should be either positional or long name
            the_only_arg = args[0]
            positional_name, long, short = _parse_arg_name(the_only_arg)
            if positional_name is not None:
                target_name = positional_name
            elif long is not None:
                target_name = long
            else:
                raise ArgumentConfigError("Could not find full name among:", args)
        elif len(args) == 2:  # should long with short name
            positional_name, long, short = _parse_arg_name(args[0])
            assert long is not None, f"Expecting --name and -n, but found: {args}"
            target_name = long

    assert target_name is not None

    return target_name


def figure_out_name_and_default_value(*args, **kwargs):
    target_name = figure_out_name(*args, **kwargs)

    assert "default" in kwargs, "Must provide default value"
    default_value = kwargs["default"]
    if "type" in kwargs:
        default_value = kwargs["type"](default_value)

    return target_name, default_value


class ArgumentConfigParser:
    _parser = None
    _parser_description = ""

    def __init__(self, *, description=None, **kwargs):
        self._groups = {}
        self._default_config = dict()
        self._config = None
        self._parser_description = description
        self._create_parser()

    def _create_parser(self):
        self._parser = ArgumentParser(
            description=self._parser_description
        )

        self._parser.add_argument("--config", default=None, help="Path to config file. All command line options will be overriden with config file content.")

    def _verify_arguments(self, args):
        return args

    def _make_config(self, args):
        return args  # .__dict__

    def _add_to_config(self, group_title, target_name, default_value):
        if group_title not in self._default_config:
            self._default_config[group_title] = {}
        self._default_config[group_title][target_name] = default_value

    def add_argument(self, *args, **kwargs):
        target_name, default_value = figure_out_name_and_default_value(*args, **kwargs)

        self._add_to_config(
            group_title="DEFAULT",
            target_name=target_name,
            default_value=default_value
        )
        self._parser.add_argument(*args, **kwargs)

    def add_argument_group(self, title, description=None):
        if title in self._groups:
            raise ArgumentConfigError("Group with such name already exist")
        group = self._parser.add_argument_group(title, description)
        self._groups[title] = _ArgumentGroup(
            parent_parser=self,
            title=title,
            argparse_group=group
        )
        return self._groups[title]

    def parse(self):
        if "--config" in sys.argv:
            config_path = sys.argv[sys.argv.index("--config") + 1]
            self.load_config(config_path)
        else:
            args = self._parser.parse_args().__dict__
            config_path = args.pop("config", None)
            self.update_config(**self._verify_arguments(args))

    def get_default_config(self):
        return deepcopy(self._default_config)

    def update_config(self, **kwargs):
        if self._config is None:
            self._config = self.get_default_config()

        recognized_options = set()

        for section, args in self._config.items():
            for key, value in kwargs.items():
                if key in args:
                    recognized_options.add(key)
                    if value is not None:
                        args[key] = value

        unrecognized = {key: value for key, value in kwargs.items() if key not in recognized_options}

        if len(unrecognized) > 0:
            raise ValueError(f"Some configuration options are not recognized: {unrecognized}")

    def get_config(self):
        if self._config is None:
            config = self.get_default_config()
        else:
            config = deepcopy(self._config)
        return config

    def reset_config(self):
        self._config = self.get_default_config()

    def save_config(self, path):
        if self._config is None:
            config = self._default_config
        else:
            config = self._config

        if len(config) == 0:
            raise ArgumentConfigError("Nothing to save. Add some values to the config.")

        yaml.dump(config, open(path, "w"))

    def load_config(self, path):
        loaded = load_config(path)
        loaded_params = {}
        for key in loaded:
            loaded_params.update(loaded[key])

        self.reset_config()
        self.update_config(**loaded_params)


class _ArgumentGroup:
    def __init__(self, parent_parser: ArgumentConfigParser, title, argparse_group):
        self._parent_parser = parent_parser
        self._title = title
        self._argparse_group = argparse_group

    def add_argument(self, *args, **kwargs):
        target_name, default_value = figure_out_name_and_default_value(*args, **kwargs)

        self._parent_parser._add_to_config(
            group_title=self._title,
            target_name=target_name,
            default_value=default_value
        )
        self._argparse_group.add_argument(*args, **kwargs)