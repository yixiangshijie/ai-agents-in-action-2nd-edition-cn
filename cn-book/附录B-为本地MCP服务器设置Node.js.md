# 附录 B 为本地 MCP 服务器设置 Node.js

许多模型上下文协议（MCP）服务器以 Node.js 包的形式在公共 npm 注册表上分发。在本地运行这些服务器最便捷的方式是使用 npx，这是一个随 Node.js 附带的命令行工具。给定一个包名，npx 会下载该包（如果尚未缓存）、解析其可执行入口点并运行它，所有这些都在一个命令中完成。这使得 MCP 客户端（如 Claude Desktop、IDE 插件或自定义智能体）无需编写任何安装脚本，即可指向一个新的 MCP 服务器。

在利用这一切之前，你需要在机器上安装一个可用的 Node.js。本附录将从头到尾指导你完成这个设置过程。它分为四个部分，遵循自然的设置顺序：安装 Node.js、验证 node 和 npx 是否在 PATH 中、使用 npx 运行一个 MCP 服务器，以及最后的故障排除和长期保持安装健康。

## B.1 安装 Node.js

Node.js 是 npx 依赖的 JavaScript 运行时，它将 npm（包管理器）和 npx 捆绑在一个安装程序中。对于本书中涵盖的 MCP 服务器，请安装 Node 20 或更高版本的当前长期支持（LTS）版本。以下小节显示了每个主要操作系统的推荐安装路径。

### B.1.1 在 Windows 上安装 Node.js

在 Windows 上，最简单的方法是使用官方安装程序：

1. 在浏览器中打开 <https://nodejs.org>，下载适用于 Windows 的 LTS 安装程序。
2. 双击下载的 .msi 文件并接受默认设置。如果你计划构建原生模块，请保持“自动安装必要工具”选项启用。否则，取消选中它是安全的。
3. 关闭并重新打开任何已打开的命令提示符或 PowerShell 窗口，以便它们获取更新的 PATH 环境变量。

如果你更喜欢并排管理多个 Node 版本，请从 <https://github.com/coreybutler/nvm-windows> 安装 nvm-windows。然后运行 `nvm install lts`，接着运行 `nvm use lts`。

### B.1.2 在 macOS 上安装 Node.js

在 macOS 上，推荐的方法是使用 Homebrew，它可以使 Node 与其他开发工具一起保持最新。在终端中运行：

brew install node

如果你没有安装 Homebrew，请先按照 <https://brew.sh> 上的说明进行操作。或者，你也可以从 <https://nodejs.org> 下载 macOS .pkg 安装程序，并像运行其他 macOS 安装程序一样运行它。

### B.1.3 在 Linux 或 WSL 上安装 Node.js

在 Linux 和 Windows Subsystem for Linux（WSL）上，推荐的方法是使用 nvm（Node Version Manager）。与发行版的系统包不同，nvm 允许你在每个项目的基础上切换 Node 版本，而无需使用 `sudo`。使用以下命令安装它：

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

关闭并重新打开你的终端，以便获取新的 shell 配置；然后安装并激活 Node 的 LTS 版本：

nvm install --lts
nvm use --lts

如果你更倾向于使用你的发行版的包管理器，Node.js 项目在 [https://github.com/nodesource/distributions](https://github.com/nodesource/distributions) 发布了官方的 APT 和 DNF 仓库。请按照该处的说明进行特定发行版的操作。

## B.2 验证你的 Node 和 npx 安装

一旦 Node 安装完成，花点时间来确认一切都在你的 PATH 中，并建立一个关于 npx 如何处理它运行的包的思维模型是值得的。以下小节涵盖了版本检查和 npx 缓存的简要介绍。

### B.2.1 检查已安装的版本

打开一个新的终端窗口并运行以下三个命令：

node --version
npm --version
npx --version

每个命令都应打印一个版本号。`node --version` 应显示 v20 或更高版本，`npm --version` 和 `npx --version` 应分别显示接近 10 的数字。如果这三个命令中的任何一个返回“命令未找到”错误，则安装程序的 PATH 更新未生效。关闭并重新打开你的终端（或整个 shell 会话），然后重试。

### B.2.2 npx 如何查找和缓存包

当你使用 npx 运行一个包时，它大致会执行以下操作：

* 它会在你的本地 node_modules 文件夹中查找该包。如果在那里找到可执行文件，它就会运行那个副本。
* 如果该包未在本地安装，它会在全局 npm 缓存中查找，位置为 ~/.npm/_npx（或 Windows 上的等效路径）。如果请求的版本已被缓存，它就会运行缓存的副本。
* 如果该包也未被缓存，npx 会从 npm 注册表下载它，将其放入缓存，然后运行它。

实际的结果是，使用 npx 首次运行 MCP 服务器的时间明显长于后续运行，因为它需要花费时间下载包。从第二次运行开始，npx 只是启动缓存的副本。

> 提示：`-y` 标志（将在下一节介绍）告诉 npx 跳过交互式的“需要安装以下包，确定？”提示。MCP 客户端将 MCP 服务器作为子进程生成，它们无法回答该提示，因此在配置客户端时始终包含 `-y`。

## B.3 使用 npx 运行 MCP 服务器

安装并验证 Node 后，你就可以运行 MCP 服务器了。以下小节将 npx 命令分解为其组成部分，然后使用官方的文件系统 MCP 服务器逐步完成一个具体示例，最后展示如何将该服务器连接到 MCP 客户端。

### B.3.1 npx 命令的构成

启动 MCP 服务器的典型 npx 命令有四个部分：

npx -y <包名> [服务器参数...]

* `npx` — 随 Node.js 附带的启动器。
* `-y` — `--yes` 的缩写。自动接受安装提示，当 MCP 客户端将服务器作为子进程生成时是必需的。
* `<包名>` — 提供 MCP 服务器的 npm 包，例如 `@modelcontextprotocol/server-filesystem`。
* `[服务器参数...]` — MCP 服务器本身接受的任何参数。这些参数会传递给服务器进程。例如，文件系统服务器接受一个或多个目录路径，MCP 客户端将被允许在这些路径中进行读写。

### B.3.2 运行文件系统 MCP 服务器

作为一个具体示例，官方的文件系统 MCP 服务器位于 npm 上的 `@modelcontextprotocol/server-filesystem`。要针对单个目录运行它，请打开一个终端并运行：

npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/directory

在 Windows 上，将 Unix 风格的路径替换为 Windows 路径，例如：

npx -y @modelcontextprotocol/server-filesystem C:\Users\you\Documents

首次运行会下载该包，可能需要几秒钟；后续运行几乎会立即启动。一旦服务器运行，它会使用 MCP 协议通过标准输入和输出与其客户端通信。直接在终端中运行它主要用作健全性检查：服务器会打印启动横幅，然后等待 stdin 上的 MCP 消息。按 Ctrl-C 停止它。

### B.3.3 将服务器连接到 MCP 客户端

MCP 客户端将其服务器作为子进程启动，这意味着你通常不会自己运行 npx 命令——而是在配置文件中向客户端描述它。该文件的确切位置取决于客户端。例如，Claude Desktop 从你用户配置文件中的一个 JSON 配置文件读取。文件系统服务器的条目如下所示：

```json
{
 "mcpServers": {
   "filesystem": {
     "command": "npx",
     "args": [
       "-y",
       "@modelcontextprotocol/server-filesystem",
       "/path/to/allowed/directory"
     ]
   }
 }
}
```

注意 `command` 字段就是 `npx`，而包名作为 `args` 条目之一出现，`-y` 列在前面以抑制安装提示。这种模式适用于在 npm 上发布的任何 MCP 服务器：更改包名和尾随参数以匹配你想要运行的服务器。

## B.4 故障排除和保持 Node 健康

大多数由 npx 启动的 MCP 服务器的问题都属于几个类别之一。以下小节涵盖了你最可能遇到的问题、如何在过时副本导致问题时清除 npx 缓存，以及如何保持 Node 本身更新。

### B.4.1 常见问题

以下是你最可能遇到的问题：

* `"npx: command not found"` — 你的 shell 找不到 Node 二进制文件。关闭并重新打开你的终端以便获取更新的 PATH。在 macOS 和 Linux 上，确认在当前 shell 中已运行 `nvm use --lts`，或将其添加到你的 shell 启动文件中。
* `EACCES` _或安装期间的权限错误_ — 你使用 `sudo` 安装了 Node，并且缓存现在归 root 所有。最干净的修复方法是移除系统范围的安装并切换到 nvm，后者将 Node 安装到你的主目录中。
* _MCP 客户端报告服务器立即退出_ — 直接在终端中运行相同的 npx 命令。服务器的错误消息会显示在那里，但通常会被客户端吞没。
* _MCP 客户端在启动时挂起_ — 你几乎肯定忘记了 `-y` 标志，并且 npx 正在等待客户端无法回答的安装确认提示。

### B.4.2 清除 npx 缓存

如果你怀疑 npx 正在运行 MCP 服务器的过时副本（例如，在包发布了你想获取的修复后），请清除缓存并让它在下次运行时重新下载：

npm cache clean --force

要在下次运行时固定特定版本，请改为在包名后附加 `@<版本>`，例如 `npx -y @modelcontextprotocol/server-filesystem@latest`。这会强制 npx 在运行前根据注册表解析请求的版本。

### B.4.3 更新 Node

Node 大约每年发布一个新的 LTS 版本。为了保持在当前的 LTS 上，请使用你安装 Node 时使用的相同工具定期更新：

* 在 Windows 上使用官方安装程序，从 <https://nodejs.org> 下载最新的 LTS .msi，然后运行它。安装程序会就地升级现有安装。
* 在 macOS 上使用 Homebrew，运行 `brew upgrade node`。
* 在 Linux、macOS 或 WSL 上使用 `nvm`，运行 `nvm install --lts`，然后运行 `nvm alias default lts/*` 以使新版本成为未来 shell 的默认版本。

升级后，再次运行 B.2.1 节中的三个版本检查，以确认新版本在你的 PATH 中。