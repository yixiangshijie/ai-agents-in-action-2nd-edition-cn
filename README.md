# AI Agents in Action (2nd Edition) | AI 智能体实战 · 第二版

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

**原书作者 (Author)**: Michael Lanham

**出版社 (Publisher)**: Manning Publications

**原书链接 (Original Book)**: [Manning - AI Agents in Action, Second Edition](https://www.manning.com/books/ai-agents-in-action-second-edition)

**GitHub 仓库**: [yixiangshijie/ai-agents-in-action-2nd-edition-cn](https://github.com/yixiangshijie/ai-agents-in-action-2nd-edition-cn)

---

## 📖 项目简介 | Project Description

本项目是《AI Agents in Action》**第二版**的中文译本，是一本智能体系统构建与应用的实战指南——目标不止于打造自主实体，更在于开发能够切实应对并解决现实问题的智能体。

全书从大语言模型（LLM）的基础应用出发，逐步深入到智能助手、多智能体系统与自主智能体的构建，系统讲解智能体系统的关键组成部分：**角色、工具与行动、知识与记忆、检索与增强、推理与规划、评估与反馈**。第二版将**五个功能层**作为组织原则，并新增 MCP 协议、测试驱动的智能体开发（TDAD）、智能体循环、认知与元认知等前沿主题，帮助开发者构建生产级智能体系统。

### 第二版与第一版

**第二版几乎是完全重写**——并非在第一版基础上的小幅修订。具体变化包括：

- **大幅更新**：新增九个面向当前实践的主题章节，移除过时内容，其余章节也用最新工具与协议全面修订
- **组织重构**：第一版提出的五个功能层概念，在第二版中更加正式化，从第 1 章即引入并作为前半部分的组织原则
- **聚焦转变**：第一版侧重解释智能体得以成立的底层概念；第二版则顺应框架发展趋势，不再纠缠内部实现细节，更聚焦如何构建能投入生产的智能体系统
- **新增专题**：专章介绍 MCP 协议与 Docker 分布式编排部署，并覆盖多智能体工作流、TDAD、RAG 智能体、深度研究智能体、智能体循环与元认知等主题

本书适合任何对智能体开发感到好奇的读者——无论你是初次构建助手，还是深入探索复杂多智能体系统，只需具备 Python 基础即可。

📖 **[在线阅读](https://yixiangshijie.github.io/ai-agents-in-action-2nd-edition-cn/)**

## **关注公众号**，获取更多AI内容：

<div align="center">
  <img src="images/wechat.jpg" alt="微信公众号二维码" width="180">
  <br>
  <sub>扫码关注，一起探索AI</sub>
</div>

---

## 📚 章节目录 | Table of Contents

- [关于本书](cn-book/0.关于本书.md)

### 第一部分：基础与核心组件 | Part One: Foundations & Core Components
- [第 1 章：AI 智能体的崛起](cn-book/1.AI智能体的崛起.md)
- [第 2 章：核心组件：大语言模型、提示词与智能体](cn-book/2.核心组件.md)

### 第二部分：协议与多智能体 | Part Two: MCP & Multi-Agent Systems
- [第 3 章：AI 智能体的 MCP 操作](cn-book/3.AI智能体的MCP操作.md)
- [第 4 章：架构与构建多智能体系统](cn-book/4.架构与构建多智能体系统.md)

### 第三部分：智能体核心能力 | Part Three: Core Agent Capabilities
- [第 5 章：智能体推理与规划](cn-book/5.智能体推理与规划.md)
- [第 6 章：为智能体处理记忆与知识 RAG](cn-book/6.为智能体处理记忆与知识RAG.md)
- [第 7 章：通过评估与反馈构建稳健的智能体](cn-book/7.通过评估与反馈构建稳健的智能体.md)

### 第四部分：部署与高级主题 | Part Four: Deployment & Advanced Topics
- [第 8 章：部署智能体与智能体系统](cn-book/8.部署智能体与智能体系统.md)
- [第 9 章：理解智能体循环](cn-book/9.理解智能体循环.md)
- [第 10 章：探索会思考、监控和适应的认知智能体](cn-book/10.探索会思考、监控和适应的认知智能体.md)
- [第 11 章：构建智能体系统的实用技巧](cn-book/11.构建智能体系统的实用技巧.md)

### 附录 | Appendices
- [附录 A：设置示例代码仓库](cn-book/附录A-设置示例代码仓库.md)
- [附录 B：为本地 MCP 服务器设置 Node.js](cn-book/附录B-为本地MCP服务器设置Node.js.md)

---

## 📖 章节内容概览 | Chapter Overview

### 🎯 第一部分：基础与核心组件

**第 1 章：AI 智能体的崛起**
- 智能体与智能体思维的定义
- 模型上下文协议（MCP）简介
- 构成智能体的五个功能层
- 从助手到智能体系统的演进

**第 2 章：核心组件：大语言模型、提示词与智能体**
- 大语言模型作为概率性令牌机器
- 通过提示工程控制 LLM 输出
- 使用 OpenAI Agents SDK 构建智能体
- 通过工具集成增强智能体能力

### 🔌 第二部分：协议与多智能体

**第 3 章：AI 智能体的 MCP 操作**
- MCP 架构：客户端、服务器与服务
- 开始使用与操作 MCP 服务器
- 构建自定义 MCP 服务器
- 使智能体与外部系统无缝交互

**第 4 章：架构与构建多智能体系统**
- 流、编排与协作的基本架构
- 平衡智能体与智能体流
- 管理智能体之间的交接
- 使用护栏验证智能体流

### ⚡ 第三部分：智能体核心能力

**第 5 章：智能体推理与规划**
- 思维链（CoT）与 ReAct 范式
- 指导智能体进行推理与规划
- 高级规划策略
- 利用顺序思考 MCP 服务器提升自主解决问题能力

**第 6 章：为智能体处理记忆与知识 RAG**
- 向量数据库与相似性搜索摄取文档
- 检索机制作为知识来源
- 检索机制作为记忆来源
- 通过 MCP 回忆之前的交互

**第 7 章：通过评估与反馈构建稳健的智能体**
- 测试驱动的智能体开发（TDAD）
- 基础化智能体与批评者智能体
- 使用 Phoenix 进行全面评估与反馈
- 构建可靠智能体的实践方法

### 🚀 第四部分：部署与高级主题

**第 8 章：部署智能体与智能体系统**
- 将智能体嵌入应用程序
- 作为微服务暴露智能体
- 使用 Docker 将智能体系统部署到生产环境
- 安全、保障与治理的关键考量

**第 9 章：理解智能体循环**
- 内部 SPAL 循环、外部任务循环与元循环
- 构建深度研究智能体
- 实现多智能体编排循环
- 构建协作智能体循环

**第 10 章：探索会思考、监控和适应的认知智能体**
- 认知与元认知作为智能体工程概念
- 认知科学理论映射到认知智能体架构
- 实现元认知过程
- 使智能体思考自身思维、监控表现并调整策略

**第 11 章：构建智能体系统的实用技巧**
- 按五个智能体层组织的实战经验
- 客户支持智能体角色指南
- RAG 智能体系统设计模式
- 深度研究智能体蓝图与综合实战示例

---

## 📖 如何使用本项目 | How to Use This Project

### 🌐 在线阅读 | Online Reading

**访问地址**: [ai-agents-in-action-2nd-edition-cn](https://yixiangshijie.github.io/ai-agents-in-action-2nd-edition-cn/)


**本地预览**：

```bash
# 方式一（推荐，macOS/Linux 自带 Python）
python3 -m http.server 3000

# 方式二（需 Node.js）
npx serve -l 3000 .
```

然后在浏览器打开 **http://localhost:3000/** 即可预览。


### 🎯 适合读者 | Target Audience

- **AI 工程师** - 构建生产级 AI 智能体系统
- **软件开发者** - 学习智能体开发技术栈
- **产品经理** - 了解智能体技术能力与应用场景
- **研究人员** - 研究智能体架构与设计模式
- **学生** - 学习 AI 智能体理论与实践

### 📚 阅读建议 | Reading Tips

1. **顺序阅读** - 建议按章节顺序阅读，前面章节是后续内容的基础
2. **动手实践** - 每章包含大量代码示例，建议实际运行体验
3. **中英对照** - 遇到难以理解的术语可对照英文原文
4. **参考查阅** - 可作为智能体开发的参考手册使用

---

## 🤝 贡献指南 | Contributing

欢迎社区贡献！你可以通过以下方式参与：

### 🔍 如何贡献 | How to Contribute

1. **错误报告** - 发现翻译错误、术语不一致或格式问题
2. **翻译改进** - 提供更优的翻译建议
3. **章节翻译** - 参与附录或章节的校对与改进
4. **校对审阅** - 帮助校对已翻译章节
5. **术语建议** - 提出术语翻译优化建议

### 📋 贡献步骤 | Contribution Steps

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/your-contribution`)
3. 提交更改 (`git commit -m 'Add: your contribution'`)
4. 推送到分支 (`git push origin feature/your-contribution`)
5. 创建 Pull Request

---

## 📄 版权信息 | Copyright

### 📖 原书版权 | Original Book Copyright

- **作者**: Michael Lanham
- **出版社**: Manning Publications
- **版权**: 原书版权归作者和出版社所有

### 🌏 翻译版权 | Translation Copyright

- **翻译**: 本翻译项目基于 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 协议开源
- **目的**: 仅用于学习交流，促进中文 AI 社区发展
- **使用限制**:
  - ✅ **允许**：自由复制、分发、展示和演绎作品（需署名译者）
  - ❌ **禁止**：任何形式的商业使用

### ⚠️ 免责声明 | Disclaimer

本翻译项目为个人学习和交流目的，不代表原书出版社或作者的官方立场。如有侵权，请联系删除。建议读者购买原版书籍以支持作者。

---

## 🔗 相关资源 | Related Resources

### 📚 学习资源 | Learning Resources

- **原书官网**: [Manning - AI Agents in Action, Second Edition](https://www.manning.com/books/ai-agents-in-action-second-edition)
- **相关代码地址**: [AI-Agent-Workflows](https://github.com/cxbxmxcx/AI-Agent-Workflows)

---

## ⭐ 支持项目 | Support the Project

如果这个项目对你有帮助，请考虑：

- 🌟 给项目加 Star
- 🍴 Fork 并参与贡献
- 📢 分享给更多需要的人
- 💝 购买原书支持作者

---

<div align="center">

**<mark>让我们一起探索 AI 智能体的无限可能！</mark>**

</div>
