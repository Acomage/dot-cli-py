import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dot.utils.file_system import FileSystem
from test.test_data.file_system_test_data import (
    test1_res,
    test2_res,
    test3_res,
    test4_res,
)


def test1():
    fs = FileSystem()
    fs.add("~/.config/nvim", "nvim")
    fs.add("~/.zshrc", "zsh")
    fs.remove("~/.config/nvim/lua/lualine/themes/ras.lua")
    print("test1:")
    print(fs.to_json() == test1_res)


def test2():
    fs = FileSystem()
    fs.add("~/.config/nvim", "nvim")
    fs.add("~/.zshrc", "zsh")
    fs.remove("~/.config/nvim/lua")
    fs.add("~/.config/nvim/lua", "nvim")
    print("test2:")
    print(fs.to_json() == test2_res)


def test3():
    fs = FileSystem()
    fs.add("~/.config/nvim/lua", "nvim")
    fs.add("~/.zshrc", "zsh")
    fs.remove("~/.config/nvim/lua/plugins/")
    fs.add("~/.config/nvim", "nvim")
    print("test3:")
    print(fs.to_json() == test3_res)


def test4():
    fs = FileSystem()
    fs.add("~/.config/nvim/lua", "nvim")
    fs.add("~/.zshrc", "zsh")
    fs.add("/etc/keyd", "keyd")
    fs.add("/etc/kmscon", "kmscon")
    fs.remove("/etc/keyd")
    print("test4:")
    print(fs.to_json() == test4_res)


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
