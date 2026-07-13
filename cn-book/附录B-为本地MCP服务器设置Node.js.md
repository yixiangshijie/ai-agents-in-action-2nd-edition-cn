# 附录 B 为本地 MCP 服务器配置 Node.js

许多模型上下文协议（Model Context Protocol，MCP）服务器都是以 Node.js 包的形式发布在公共 npm 仓库中的。在本地运行这些服务器最方便的方法是使用 `npx`——一个随 Node.js 一同提供的小型命令行工具。给定一个包名后，`npx` 会自动下载该包（如果尚未缓存）、解析其可执行入口，并在一条命令中直接运行它。借助这一机制，你可以让 Claude Desktop、IDE 插件或自定义智能体等 MCP 客户端直接连接到一个全新的 MCP 服务器，而无需自己编写任何安装脚本。

在使用这些功能之前，你需要确保机器上已经安装了可用的 Node.js 环境。本附录将完整介绍整个配置流程。内容分为四个部分，并按照自然的配置顺序组织：安装 Node.js、验证 `node` 和 `npx` 是否已加入 PATH、使用 `npx` 运行 MCP 服务器，以及最后排查常见问题并长期维护你的安装环境。

## B.1 安装 Node.js

Node.js 是 `npx` 所依赖的 JavaScript 运行时，并且它会通过同一个安装程序同时安装 `npm`（包管理器）和 `npx`。对于本书涉及的 MCP 服务器，建议安装 Node 20 或更高版本的长期支持版（LTS）。以下小节分别介绍各主流操作系统推荐的安装方式。

### B.1.1 在 Windows 上安装 Node.js

在 Windows 上，最简单的方法是使用官方安装程序：

1. 使用浏览器打开 <https://nodejs.org>，下载适用于 Windows 的 LTS 安装包。
2. 双击下载的 `.msi` 文件，并使用默认选项完成安装。如果你计划编译原生模块（native modules），请保持“Automatically Install the Necessary Tools（自动安装必要工具）”选项处于启用状态；否则，可以取消勾选。
3. 关闭并重新打开所有命令提示符（Command Prompt）或 PowerShell 窗口，以便它们重新加载更新后的 `PATH` 环境变量。

如果你希望同时管理多个 Node 版本，可以安装 `nvm-windows`：

<https://github.com/coreybutler/nvm-windows>

安装完成后，执行以下命令：

```bash
nvm install lts
nvm use lts
```

### B.1.2 在 macOS 上安装 Node.js

在 macOS 上，推荐使用 Homebrew，因为它能够与你的其他开发工具一起保持 Node 的更新。在终端中执行：

```bash
brew install node
```

如果尚未安装 Homebrew，请先访问以下地址并按照说明完成安装：

<https://brew.sh>

或者，你也可以从以下网站下载 macOS 的 `.pkg` 安装包，并像安装其他 macOS 软件一样完成安装：

<https://nodejs.org>

### B.1.3 在 Linux 或 WSL 上安装 Node.js

在 Linux 和 Windows Subsystem for Linux（WSL）环境中，推荐使用 Node Version Manager（`nvm`）。

与发行版自带的软件包不同，`nvm` 允许你按项目切换 Node 版本，而无需使用 `sudo`。

执行以下命令安装：

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

关闭并重新打开终端，使新的 Shell 配置生效。然后安装并启用 Node 的 LTS 版本：

```bash
nvm install --lts
nvm use --lts
```

如果你更喜欢使用发行版自带的包管理器，Node.js 项目也提供了官方的 APT 和 DNF 软件源：

<https://github.com/nodesource/distributions>

请根据你的发行版，参考该仓库中的具体说明完成安装。

## B.2 验证 Node 和 npx 安装

安装完成后，建议花一点时间确认相关命令已经加入 `PATH`，并建立对 `npx` 如何处理软件包的基本认知。

以下小节将介绍版本检查方法，以及 `npx` 缓存机制的工作原理。

### B.2.1 检查已安装版本

打开一个新的终端窗口，并执行以下三个命令：

```bash
node --version
npm --version
npx --version
```

每条命令都应输出一个版本号。

* `node --version` 应返回 `v20` 或更高版本。
* `npm --version` 和 `npx --version` 应返回接近 `10` 的版本号。

如果其中任意一个命令返回“Command Not Found（命令未找到）”错误，则说明安装程序对 `PATH` 的更新尚未生效。请关闭并重新打开终端（必要时重启整个 Shell 会话），然后再次尝试。

### B.2.2 npx 如何查找和缓存软件包

当你使用 `npx` 运行一个软件包时，它大致会执行以下步骤：

* 首先检查当前项目的 `node_modules` 目录。如果在那里找到可执行文件，就直接运行该副本。
* 如果本地未安装，则检查全局 npm 缓存目录 `~/.npm/_npx`（Windows 上为对应目录）。如果请求的版本已经缓存，则直接运行缓存副本。
* 如果缓存中也不存在，则从 npm 仓库下载软件包，将其放入缓存后再运行。

这意味着：第一次使用 `npx` 启动 MCP 服务器时，速度通常会明显较慢，因为它需要下载软件包。而从第二次开始，`npx` 会直接运行缓存版本，因此启动速度会快很多。

> **提示：** `-y` 参数（将在下一节介绍）会让 `npx` 自动跳过“Need to install the following packages, ok?” 的交互式确认提示。由于 MCP 客户端在以子进程方式启动 MCP 服务器时无法回答该提示，因此在配置 MCP 客户端时，应始终添加 `-y` 参数。

## B.3 使用 npx 运行 MCP 服务器

当 Node 安装并验证完成后，你就可以运行 MCP 服务器了。

以下小节将首先拆解 `npx` 命令的组成部分，然后使用官方的 Filesystem MCP Server 作为示例，最后介绍如何将该服务器接入 MCP 客户端。

### B.3.1 npx 命令结构

使用 `npx` 启动 MCP 服务器的典型命令如下：

```bash
npx -y <package-name> [server-arguments...]
```

其组成部分如下：

* `npx` —— Node.js 自带的启动器。
* `-y` —— `--yes` 的缩写。自动接受安装提示，这是 MCP 客户端以子进程方式启动服务器时的必需参数。
* `<package-name>` —— 提供 MCP 服务器的 npm 软件包名称，例如 `@modelcontextprotocol/server-filesystem`。
* `[server-arguments...]` —— MCP 服务器本身支持的参数，这些参数会原样传递给服务器进程。例如，Filesystem MCP Server 接收一个或多个目录路径，用于指定 MCP 客户端可以读写的目录范围。

### B.3.2 运行 Filesystem MCP Server

作为一个具体示例，官方的 Filesystem MCP Server 在 npm 上的包名为 `@modelcontextprotocol/server-filesystem`。要让它对单个目录提供服务，请打开终端并执行：

```bash
npx -y @modelcontextprotocol/server-filesystem /path/to/allowed/directory
```

在 Windows 上，请将 Unix 风格路径替换为 Windows 路径，例如：

```bash
npx -y @modelcontextprotocol/server-filesystem C:\Users\you\Documents
```

第一次运行时需要下载软件包，因此可能需要几秒钟；之后再次运行时，通常会立即启动。

服务器启动后，会通过标准输入（stdin）和标准输出（stdout）使用 MCP 协议与客户端进行通信。直接在终端中运行它主要用于确认环境是否正常：服务器会输出启动信息，然后等待来自 stdin 的 MCP 消息。

按下 `Ctrl-C` 即可停止服务器。

### B.3.3 将服务器接入 MCP 客户端

MCP 客户端会以子进程（subprocess）的形式启动 MCP 服务器，因此通常情况下，你不需要自己执行 `npx` 命令，而是需要在客户端配置文件中描述该命令。

配置文件的位置取决于具体客户端。例如，Claude Desktop 会从用户目录下的 JSON 配置文件中读取 MCP 配置。

Filesystem MCP Server 的配置示例如下：

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

请注意：

* `command` 字段仅填写 `npx`。
* 包名作为 `args` 中的一个参数传入。
* `-y` 必须放在最前面，以避免出现安装确认提示。

这一模式适用于所有发布到 npm 的 MCP 服务器：只需要替换包名以及后续参数，即可启动你需要的 MCP 服务。

## B.4 排查问题并保持 Node 环境健康

通过 `npx` 启动 MCP 服务器时，大多数问题都属于少数几个固定类别。

以下小节将介绍最常见的问题、如何清理 `npx` 缓存，以及如何保持 Node 本身处于最新状态。

### B.4.1 常见问题

以下是你最可能遇到的问题：

* `npx: command not found`
  
  当前 Shell 无法找到 Node 可执行文件。请关闭并重新打开终端，使更新后的 `PATH` 生效。

  在 macOS 和 Linux 上，请确认当前 Shell 已执行：

  ```bash
  nvm use --lts
  ```

  或将该命令加入 Shell 启动文件（例如 `.bashrc`、`.zshrc`）。

* 安装过程中出现 `EACCES` 或权限错误

  这通常意味着你使用 `sudo` 安装了 Node，导致缓存目录属于 `root` 用户。

  最干净的解决方案是卸载系统级安装，并改用 `nvm`，因为它会将 Node 安装到用户目录中。

* MCP 客户端报告“服务器立即退出”

  请直接在终端中执行同样的 `npx` 命令。

  MCP 服务器输出的错误信息通常会显示在终端中，但客户端往往会吞掉这些信息，因此无法直接看到。

* MCP 客户端启动时卡住

  几乎可以肯定是忘记添加 `-y` 参数。

  此时，`npx` 正在等待安装确认提示，而 MCP 客户端无法响应该交互，因此会一直卡住。

### B.4.2 清理 npx 缓存

如果你怀疑 `npx` 正在运行 MCP 服务器的旧版本（例如软件包已经发布了修复，而你希望立即使用最新版本），可以清理缓存，并在下次运行时重新下载：

```bash
npm cache clean --force
```

如果你希望固定使用某个特定版本，可以在包名后追加 `@<version>`，例如：

```bash
npx -y @modelcontextprotocol/server-filesystem@latest
```

这样会强制 `npx` 在运行前到 npm 仓库解析并获取指定版本。

### B.4.3 更新 Node

Node 大约每年发布一个新的 LTS 版本。为了始终保持使用当前的长期支持版，建议定期更新。

更新方式取决于你的安装方式：

* 如果是在 Windows 上通过官方安装包安装，请访问：

  <https://nodejs.org>

  下载最新的 LTS `.msi` 文件并运行。安装程序会自动覆盖现有版本。

* 如果在 macOS 上使用 Homebrew，请执行：

```bash
brew upgrade node
```

* 如果在 Linux、macOS 或 WSL 上使用 `nvm`，请执行：

```bash
nvm install --lts
nvm alias default lts/*
```

上述命令会安装新的 LTS 版本，并将其设置为未来所有 Shell 会话的默认版本。

升级完成后，请再次执行 B.2.1 节中的三个版本检查命令，以确认新的 Node、npm 和 npx 已正确加入 `PATH` 环境变量。