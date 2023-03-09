import os
import sys


def test_parser():
    from nhcli import ArgumentConfigParser, ArgumentConfigError

    args = ArgumentConfigParser()

    try:
        args.save_config("save.yaml")
        assert False
    except ArgumentConfigError:
        pass

    args.add_argument("positional_arg", default=None)
    args.add_argument("--optional_arg1", default=1, type=int)
    args.add_argument("--optional_arg2", "-oa2", default=1, type=int)
    try:
        args.add_argument("-o2", default=None, type=str)
        assert False, "Exception was not caught"
    except ArgumentConfigError:
        pass
    args.add_argument("--optional_arg3", dest="arg3", default=1.0, type=float)

    group = args.add_argument_group("GROUP1")
    group.add_argument("--optional_group1", default=1, type=int)
    group.add_argument("positional_group1", default=1)

    try:
        group = args.add_argument_group("GROUP1")
        assert False
    except ArgumentConfigError:
        pass
    group = args.add_argument_group("GROUP2")
    group.add_argument("--optional_group2", default=1, type=int)
    group.add_argument("positional_group2", default=None)

    default_config_ = args.get_config()
    sys.argv = [
        "",
        "--optional_arg1", "0",
        "--optional_arg2", "0",
        "--optional_arg3", "0",
        "--optional_group2", "0",
        "positional",  # positional_arg
        "1",  # positional_group1
        "some",  # positional_group2
    ]

    args.parse()

    config_parsed = args.get_config()
    default_config = args.get_default_config()

    assert default_config_ == default_config
    assert config_parsed != default_config

    assert config_parsed["DEFAULT"]['positional_arg'] == 'positional'
    assert config_parsed["DEFAULT"]['optional_arg1'] == 0
    assert config_parsed["DEFAULT"]['optional_arg2'] == 0
    assert config_parsed["DEFAULT"]['arg3'] == 0.0 and type(config_parsed["DEFAULT"]['arg3']) == float

    assert config_parsed['GROUP1']['optional_group1'] == 1 and type(config_parsed['GROUP1']['optional_group1']) == int
    assert config_parsed['GROUP1']['positional_group1'] == "1"

    assert config_parsed['GROUP2']['optional_group2'] == 0
    assert config_parsed['GROUP2']['positional_group2'] == "some"

    args.update_config(optional_group1=0)
    config_parsed = args.get_config()
    assert config_parsed['GROUP1']['optional_group1'] == 0

    args.save_config("saved.yaml")
    args.load_config("saved.yaml")
    restored_config  = args.get_config()
    assert restored_config == config_parsed
    os.remove("saved.yaml")


if __name__ == "__main__":
    test_parser()