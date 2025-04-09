import os

# variables that can be set by the user
REPOPATH = os.path.expanduser("~/.dotfiles")
DEFAULT_LANGUAGE = "en"
MAGIC_STRING = "hello world"

## Variables that should not be changed by the user
VARIABLES_PATH = os.path.abspath(__file__)
USERPATH = os.path.expanduser("~")
SYSTEMPATH = "/"
REPO_USER_PATH = os.path.join(REPOPATH, "user")
REPO_SYSTEM_PATH = os.path.join(REPOPATH, "system")
REPO_CONFIG_PATH = os.path.join(REPOPATH, "config.json")
REPO_LOCAL_CONFIG_PATH = os.path.join(REPOPATH, "local_config.json")

MESSAGES_PATH = "rewrite_by_hand.data.i18n"

README_ORIGIN = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "README.md"
)
with open(README_ORIGIN, "r") as f:
    README_FIRST_LINE = f.readline().strip()
CONFIG_ORIGIN = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "config.json"
)
IGNORE_ORIGIN = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "ignore"
)
