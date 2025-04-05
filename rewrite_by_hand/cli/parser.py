import argparse

# from rewrite_by_hand.cli.commands import (
#     # cmd_init,
#     cmd_add,
#     cmd_remove,
#     # cmd_edit,
#     # cmd_apply,
#     # cmd_sync,
#     # cmd_diff,
#     # cmd_push,
#     # cmd_pull,
#     # cmd_update,
#     # cmd_remote,
#     # cmd_manage,
#     # cmd_conflict,
#     # cmd_clean,
# )
from rewrite_by_hand.cli.commands.init import cmd_init
from rewrite_by_hand.cli.commands.add import cmd_add
# from rewrite_by_hand.cli.commands.remove import cmd_remove

from rewrite_by_hand.cli.commands.clean import cmd_clean


def create_parser() -> argparse.ArgumentParser:
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="dot",
        description="Dot: A simple dotfile management tool for Linux systems.",
        epilog="For more information, visit https://github.com/Acomage/dot-cli-py",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Make subcommands required
    subparsers.required = True

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a dotfiles repository")
    init_parser.add_argument(
        "url", nargs="?", help="URL of a remote repository to clone"
    )
    init_parser.set_defaults(func=cmd_init)

    # add command
    add_parser = subparsers.add_parser(
        "add", help="Add a file or directory to the repository"
    )
    add_parser.add_argument("path", help="Path to the file or directory")
    add_parser.add_argument("software", help="Name of the software the file belongs to")
    add_parser.add_argument("--pure", action="store_true", help="Add without managing")
    add_parser.set_defaults(func=cmd_add)

    # remove command
    # remove_parser = subparsers.add_parser(
    #     "remove", help="Remove a file or directory from the repository"
    # )
    # remove_parser.add_argument("path", help="Path to the file or directory")
    # remove_parser.add_argument(
    #     "software", help="Name of the software the file belongs to"
    # )
    # remove_parser.set_defaults(func=cmd_remove)

    # edit command
    # edit_parser = subparsers.add_parser("edit", help="Edit a file in the repository")
    # edit_parser.add_argument("path", help="Path to the file")
    # edit_parser.set_defaults(func=cmd_edit)
    #
    # # apply command
    # apply_parser = subparsers.add_parser(
    #     "apply", help="Apply changes from the repository to the system"
    # )
    # apply_parser.add_argument("path", nargs="?", help="Path to the file or directory")
    # apply_parser.add_argument("--all", action="store_true", help="Apply all changes")
    # apply_parser.set_defaults(func=cmd_apply)
    #
    # # sync command
    # sync_parser = subparsers.add_parser(
    #     "sync", help="Sync changes from the system to the repository"
    # )
    # sync_parser.add_argument("path", nargs="?", help="Path to the file or directory")
    # sync_parser.add_argument("--all", action="store_true", help="Sync all changes")
    # sync_parser.set_defaults(func=cmd_sync)
    #
    # # diff command
    # diff_parser = subparsers.add_parser(
    #     "diff", help="Show differences between system and repository"
    # )
    # diff_parser.add_argument("path", nargs="?", help="Path to the file or directory")
    # diff_parser.set_defaults(func=cmd_diff)
    #
    # # push command
    # push_parser = subparsers.add_parser(
    #     "push", help="Push changes to the remote repository"
    # )
    # push_parser.set_defaults(func=cmd_push)
    #
    # # pull command
    # pull_parser = subparsers.add_parser(
    #     "pull", help="Pull changes from the remote repository"
    # )
    # pull_parser.set_defaults(func=cmd_pull)
    #
    # # update command
    # update_parser = subparsers.add_parser(
    #     "update", help="Update the system with changes from the remote repository"
    # )
    # update_parser.set_defaults(func=cmd_update)
    #
    # # remote command
    # remote_parser = subparsers.add_parser("remote", help="Manage the remote repository")
    # remote_parser.add_argument("url", nargs="?", help="URL of the remote repository")
    # remote_parser.add_argument(
    #     "--clean", action="store_true", help="Remove the remote repository"
    # )
    # remote_parser.set_defaults(func=cmd_remote)
    #
    # # manage command
    # manage_parser = subparsers.add_parser(
    #     "manage", help="Manage software configurations"
    # )
    # manage_parser.add_argument("software", help="Name of the software to manage")
    # manage_parser.set_defaults(func=cmd_manage)
    #
    # # conflict command
    # conflict_parser = subparsers.add_parser(
    #     "conflict", help="Manage conflicts between machines"
    # )
    # conflict_parser.add_argument("path", help="Path to the file")
    # conflict_parser.add_argument(
    #     "--clean", action="store_true", help="Remove conflict markers"
    # )
    # conflict_parser.set_defaults(func=cmd_conflict)
    #
    # clean command
    clean_parser = subparsers.add_parser("clean", help="Clean up the repository")
    clean_parser.set_defaults(func=cmd_clean)

    return parser
