# 附录 A 设置示例代码仓库

本书的配套代码仓库托管了各章节对应的示例代码。它展示了如何使用 OpenAI 的工具和 API 来构建和运行 AI 智能体，并按照章节进行组织，每章的示例都存放在独立的文件夹中。在学习书中的代码清单之前，你需要在自己的机器上拥有该仓库的工作副本、一个符合示例要求的 Python 环境，以及一个通过本地环境文件连接的有效 OpenAI API Key。

本附录将完整介绍整个环境配置流程。内容分为四个部分，并按照自然的配置顺序进行组织：克隆代码仓库、创建 Python 环境、安装依赖并配置 API Key，以及最后运行一个示例智能体来确认所有配置均已正确完成。第一次配置时，请按照章节顺序依次执行；之后再次查阅时，可以直接跳转到你需要的步骤。

## A.1 克隆代码仓库

首先，将代码仓库克隆到本地机器。该仓库托管在 GitHub 上，可以通过标准的 `git clone` 命令获取。打开终端，切换到你存放项目的目录，然后执行以下命令：

```bash
git clone https://github.com/cxbxmxcx/AI-Agent-Workflows.git
cd AI-Agent-Workflows
```

第一条命令会将整个仓库下载到一个新的 `AI-Agent-Workflows` 文件夹中。第二条命令则进入该目录，以确保后续的配置步骤都在正确的位置执行。

## A.2 创建 Python 环境

该项目要求使用 Python 3.11 或更高版本。推荐做法是为该仓库创建一个专用的虚拟环境，以避免其依赖与机器上的其他 Python 项目发生冲突。由于不同操作系统的命令有所差异，因此下面分别给出 Windows 和 macOS/Linux 的操作说明。

在 Windows 上，请在仓库根目录打开命令提示符（Command Prompt）或 PowerShell，然后执行：

```bash
python -m venv venv
venv\Scripts\activate
```

在 macOS 或 Linux 上，请在仓库根目录打开终端，并执行：

```bash
python3 -m venv venv
source venv/bin/activate
```

无论使用哪种平台，当虚拟环境成功激活后，你的命令提示符前都会显示 `(venv)` 前缀，这意味着后续执行的 `python` 和 `pip` 命令都将在该虚拟环境中运行。

如果你更倾向于使用现有的 Python 安装，而不是前面创建的虚拟环境，也可以将 VS Code 指向对应的解释器。具体步骤如下：

1. 按下 `Ctrl-Shift-P`（Windows/Linux）或 `Cmd-Shift-P`（macOS）打开命令面板（Command Palette）。
2. 搜索 `Python: Select Interpreter`。
3. 选择你希望用于本项目的 Python 解释器。

## A.3 安装依赖并配置环境

在拥有可用的 Python 环境后，下一步是安装示例代码所依赖的软件包，并为其配置 OpenAI API Key。该仓库在根目录下通过 `requirements.txt` 固定依赖版本，并通过本地 `.env` 文件读取 API Key。本节将分别介绍两种安装方式以及 API Key 的配置方法。

### A.3.1 路径 A：使用 VS Code 调试器

如果你已经安装了 VS Code 及其 Python 扩展，可以直接按下 `F5` 来调试某个示例文件。仓库附带的启动配置（launch configuration）会确保在运行示例之前自动安装所需依赖。

如果你不想手动管理依赖，这是最快捷的方式。

### A.3.2 路径 B：使用 pip 手动安装

如果你更喜欢自行安装依赖，或者希望直接在终端中运行示例，请确保虚拟环境已激活，并在仓库根目录执行以下命令：

```bash
pip install -r requirements.txt
```

`pip` 会下载所有固定版本的软件包，并将其安装到当前激活的虚拟环境中。根据你的网络情况，首次安装可能需要一到两分钟。

### A.3.3 配置 OpenAI API Key

这些示例通过读取仓库根目录中的 `.env` 文件来获取 OpenAI API Key。仓库提供了一个 `.env.example` 文件，你可以复制它作为起始模板。

请在仓库根目录创建一个名为 `.env` 的文件，并填写以下内容：

```text
OPENAI_API_KEY=your_openai_api_key_here
```

将 `your_openai_api_key_here` 替换为你自己的 OpenAI API Key。你可以通过 OpenAI API Keys 页面获取密钥：

<https://platform.openai.com/account/api-keys>

**警告：** 切勿共享或将 `.env` 文件提交到版本控制系统。该文件包含能够访问你 OpenAI 账户的敏感凭证，任何获得该密钥的人都可能在你的账户上产生费用。

## A.4 运行示例代码

当代码仓库已经克隆完成、虚拟环境已激活、依赖安装完毕，并且 API Key 已正确配置后，你就可以运行示例程序了。本节将介绍如何运行示例、处理最常见的问题，以及一些有助于在阅读本书期间保持环境稳定的小习惯。

### A.4.1 运行示例

每章的代码都位于仓库根目录下对应的章节文件夹中。要运行某个示例，请进入对应章节目录并执行相应的 Python 文件。例如，要运行第 2 章中的第一个智能体：

```bash
python chapter_02/01_first_agent.py
```

智能体会执行完整个流程，并将输出打印到终端中。对于仓库中的其他示例，你只需要按照相同模式，将路径替换为对应的章节和文件名即可。

### A.4.2 排查常见问题

大多数配置问题通常都源于以下两个原因之一：API Key 缺失或错误，或者当前激活的 Python 解释器不正确。以下两种情况几乎涵盖了你可能遇到的大多数问题：

* 如果看到认证错误（authentication error），请确认 `.env` 文件位于仓库根目录，并确保 `OPENAI_API_KEY` 设置为有效的 API Key。
* 如果看到 `ModuleNotFoundError`，请确认虚拟环境已经激活，并且依赖已经安装到该虚拟环境中。

### A.4.3 保持环境健康

在阅读本书剩余内容时，养成以下几个小习惯可以帮你节省大量时间：

* 确保当前使用的 Python 解释器确实对应于你配置的环境。将系统 Python 与项目虚拟环境混用，是导致导入错误（import error）的最常见原因。
* `.env` 文件已经被列入 `.gitignore`，永远不应提交到版本控制系统。请将其保留在本地，以确保 API Key 的安全。
* 如果你因任何原因轮换（rotate）了 OpenAI API Key，请在再次运行示例之前，及时更新 `.env` 文件中的值。