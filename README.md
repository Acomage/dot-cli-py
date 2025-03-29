# DON'T USE THIS TOOL NOW

This tool is not ready for use, it's still under development. There are many bugs and missing features. I will update this README when it's ready for use.

# 现在不要使用这个工具

这个工具还没有准备好使用，仍在开发中。有很多bug和缺失的功能。当它准备好使用时，我会更新这个README。

# Dot CLI

A powerful dotfile management tool for Linux systems.

## Overview

Dot CLI helps you manage your dotfiles across multiple machines. It provides features for tracking, synchronizing, and maintaining configuration files with support for machine-specific configurations.

## Features

- Manage configuration files from multiple software applications
- Track files from both user home directory and system directories
- Support for machine-specific configurations via conflict markers
- Git integration for easy backup and synchronization
- Cross-machine dotfile deployment
- Simple command-line interface

## Installation

### Requirements

- Python 3.7+
- Git

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/Acomage/dot-cli-py.git

# Set up to use
cd dot-cli-py
chmod +x main.py
# Add the following line to your .bashrc or .zshrc or .config/fish/config.fish, or run it every time you open a shell session
alias dot="python /path/to/your/main.py"
```

## Quick Start

### Initialize a New Repository

```bash
# Create a new dotfiles repository in ~/.dotfiles
dot init
```

### Add Configuration Files

```bash
# Add your .zshrc file and track it as "zsh"
dot add ~/.zshrc zsh

# Add your Neovim config directory and track it as "nvim"
dot add ~/.config/nvim nvim
```

### Edit Files in the Repository

```bash
# Edit your .zshrc in the repository
dot edit ~/.zshrc
```

### Apply Changes to Your System

```bash
# Apply changes to your system
dot apply ~/.zshrc
```

### Set Up Remote Repository

```bash
# Connect to a GitHub repository
dot remote https://github.com/yourusername/dotfiles.git

# Push your changes
dot push
```

### Clone on Another Machine

```bash
# On a new machine, clone and set up your dotfiles
dot init https://github.com/yourusername/dotfiles.git

# Choose which software configurations to use on this machine
dot manage zsh
dot manage nvim

# Apply the configurations
dot apply --all
```

## Machine-Specific Configurations

Sometimes you need different settings on different machines. Dot handles this with conflict markers:

```bash
# Mark a file as having machine-specific configurations
dot conflict ~/.config/alacritty/alacritty.yml

# Edit the conflict file (in the editor, wrap machine-specific parts with markers)
# Example:
# //YuriSaveTheWorld font_size: 16
# Or for blocks:
# /*YuriSaveTheWorld
# background_opacity: 0.9
# YuriSaveTheWorld*/
```

## Usage

```
dot init [url]              Initialize a dotfiles repository
dot add <path> <software>   Add a file to the repository
dot remove <path> <software> Remove a file from the repository
dot edit <path>             Edit a file in the repository
dot apply [path]            Apply repository changes to the system
dot sync [path]             Sync system changes to the repository
dot diff [path]             Show differences between system and repository
dot push                    Push changes to the remote repository
dot pull                    Pull changes from the remote repository
dot update                  Update system with changes from remote
dot remote [url]            Set the remote repository URL
dot manage <software>       Add software to local configuration
dot conflict <path>         Manage conflict markers for a file
dot clean                   Clean up the repository
```

## Language Support

Dot CLI supports both English and Chinese. Set the `DOT_LANGUAGE` environment variable to your preferred language:

```bash
# English (default)
export DOT_LANGUAGE=en

# Chinese
export DOT_LANGUAGE=zh
```

---

# Dot CLI

Linux系统强大的点文件管理工具。

## 概述

Dot CLI帮助您跨多台机器管理点文件（dotfiles）。它提供了跟踪、同步和维护配置文件的功能，并支持机器特定的配置。

## 功能

- 管理来自多个软件应用程序的配置文件
- 跟踪用户主目录和系统目录中的文件
- 通过冲突标记支持机器特定的配置
- Git集成，易于备份和同步
- 跨机器点文件部署
- 简单的命令行界面

## 安装

### 要求

- Python 3.7+
- Git

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/Acomage/dot-cli-py.git

# 设置使用
cd dot-cli-py
chmod +x main.py
# 将以下行添加到您的.bashrc或.zshrc或.config/fish/config.fish中，或者每次打开shell会话时运行它
alias dot="python /path/to/your/main.py"
```

## 快速入门

### 初始化新仓库

```bash
# 在~/.dotfiles中创建新的dotfiles仓库
dot init
```

### 添加配置文件

```bash
# 添加.zshrc文件并将其跟踪为"zsh"
dot add ~/.zshrc zsh

# 添加Neovim配置目录并将其跟踪为"nvim"
dot add ~/.config/nvim nvim
```

### 编辑仓库中的文件

```bash
# 在仓库中编辑.zshrc
dot edit ~/.zshrc
```

### 将更改应用到系统

```bash
# 将更改应用到系统
dot apply ~/.zshrc
```

### 设置远程仓库

```bash
# 连接到GitHub仓库
dot remote https://github.com/yourusername/dotfiles.git

# 推送更改
dot push
```

### 在另一台机器上克隆

```bash
# 在新机器上，克隆并设置dotfiles
dot init https://github.com/yourusername/dotfiles.git

# 选择在此机器上使用哪些软件配置
dot manage zsh
dot manage nvim

# 应用配置
dot apply --all
```

## 机器特定配置

有时您需要在不同机器上使用不同的设置。Dot使用冲突标记处理这种情况：

```bash
# 将文件标记为具有机器特定配置
dot conflict ~/.config/alacritty/alacritty.yml

# 编辑冲突文件（在编辑器中，用标记包装机器特定部分）
# 示例：
# //YuriSaveTheWorld font_size: 16
# 或者对于块：
# /*YuriSaveTheWorld
# background_opacity: 0.9
# YuriSaveTheWorld*/
```
