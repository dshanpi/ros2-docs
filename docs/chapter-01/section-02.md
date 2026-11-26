---
title: "1.2 系统环境介绍"
sidebar_label: "1.2 系统环境介绍"
slug: /chapter-01/section-02/
---

## 1.2.1 BianbuOS简介

Bianbu是一个针对 RISC-V 架构处理器深度优化的操作系统，基于 Ubuntu 社区源码构建，旨在为开发者和客户提供高效、稳定的系统解决方案。Bianbu 提供多个版本，包括桌面版（Bianbu Desktop）和 NAS 版，适用于不同的产品领域。本套课程使用Bianbu Desktop版本。

1. <strong>核心特点</strong>

Bianbu具有以下核心特点：

1. <strong>深度优化</strong>

- 针对 RISC-V 架构处理器进行深度优化，提供高性能和低功耗的系统支持。

- 支持多核处理器和硬件加速功能，适合 AI、边缘计算和多媒体处理等场景。

2. <strong>简洁、快速、安全</strong>

- 提供简洁的桌面环境，支持快速启动和流畅运行。

- 集成安全功能，确保系统和数据的安全性。

3. <strong>丰富的软件生态</strong>

- 支持标准的 Debian 软件包格式，通过 APT 软件源管理组件。

- 提供多种应用、框架、运行时和库，包括 GNOME 桌面、Chromium 浏览器、LibreOffice 办公套件、Visual Studio Code、Docker 等。

4. <strong>硬件支持</strong>

- 支持多种 RISC-V 平台，包括 BPI-F3、Milk-V Jupiter、MUSE Card、MUSE Pi、MUSE Box 和 MUSE Book。

- 提供完整的硬件驱动支持，确保系统与硬件的无缝集成。

5. <strong>开源与社区支持</strong>

- 源码开放，支持社区贡献和定制化开发。

- 提供详细的文档和技术支持，方便开发者快速上手。

2. <strong>系统架构</strong>

Bianbu 的系统架构包括多个层次，如图1.3所示：

[![图1.3 BianbuOS系统结构图](/img/manual/image10.png)](/img/manual/image10.png)

*图1.3 BianbuOS系统结构图*

- 应用层：提供桌面环境和常用应用。

- 框架层：支持多种应用框架（如Electron、GTK、QT）和多媒体框架（如FFmpeg、GStreamer）。

- 运行时层：支持多种编程语言的运行时环境（如Python、Java、Node.js、Rust）。

- 库层：提供硬件加速的库（如OpenCV、OpenSSL）和多媒体处理平台（如MPP）。

- 内核层：基于Linux内核（版本6.6），负责硬件资源管理和系统功能。

- 引导层：包括U-Boot和OpenSBI，负责系统启动和硬件初始化。

## 1.2.2 硬件与软件开发环境

下面将介绍MUSE-PI-PRO硬件与软件开发环境，涵盖从代码编辑到程序调试的各类工具，先帮助大家简单了解开发所需的基础工具，后面将详细讲解使用。

1. <strong>开发工具</strong>

- <strong>VS Code：</strong>作为一款轻量且功能强大的跨平台代码编辑器，VS Code 凭借丰富的插件生态，为嵌入式开发提供了一站式支持。通过安装 C/C++ 插件，可实现代码语法高亮、智能补全与错误检查；配合 Remote - SSH 插件，能够便捷地远程连接嵌入式开发板，直接在本地编辑器中编辑板端文件，极大提升开发效率。此外，其内置的调试功能与 Git 版本控制集成，便于开发者进行代码调试与版本管理。

Vscode访问链接：<a href="https://code.visualstudio.com/">https://code.visualstudio.com/</a>

- <strong>MobaXterm:</strong> MobaXterm是一款功能强大的跨平台终端软件，不仅支持SSH、RDP等多种远程连接协议，还特别适用于嵌入式开发场景，其串口连接功能极为便捷。用户可通过直观的设置界面快速配置波特率、数据位等参数，建立与开发板、单片机等串口设备的稳定连接，实现全双工数据传输，同时还能实时查看数据交互、记录日志，配合多标签界面可同时管理多个串口会话，结合文件传输等其他功能，全方位提升开发调试效率。

MobaXterm访问连接：<a href="https://mobaxterm.mobatek.net/">https://mobaxterm.mobatek.net/</a>

- <strong>VSCodium：</strong>VSCodium是VSCode的开源替代品，保留了 VS Code 的核心功能，且具备通过 SSH 直接连接板子的能力。对于注重开源协议或存在版权限制的开发场景，VSCodium 提供了更灵活的选择。开发者可以像使用 VS Code 一样，在本地界面中对开发板进行代码编写、调试与管理，实现高效的远程开发流程。（该软件可以SSH连接本套课程使用的主板MUSE\_PI\_PRO）

VSCodium访问连接：<a href="https://github.com/VSCodium/vscodium">https://github.com/VSCodium/vscodium</a>

2. <strong>编译器</strong>

GCC（GNU Compiler C	ollection）是嵌入式开发中应用广泛的编译器套件，支持C、C++、Objective - C等多种编程语言。针对嵌入式设备的特殊性，GCC 提供了交叉编译功能，允许开发者在x86架构的主机上编译出适用于ARM、RISC-V等嵌入式架构的可执行代码。通过配置不同的交叉编译工具链，如arm-none-eabi-gcc，开发者可以精确控制编译过程中的优化等级、目标平台特性与链接脚本，生成高效且适配目标硬件的二进制文件，为嵌入式程序的运行提供坚实基础。

3. <strong>调试工具</strong>

GDB（GNU Debugger）是GNU项目中功能强大的程序调试器，常用于嵌入式系统的软件开发调试。在嵌入式开发场景下，GDB可通过JTAG、串口或网络等方式与目标开发板建立连接，实现对程序的断点调试、变量查看、堆栈跟踪等操作。开发者可以在程序运行过程中暂停执行，检查关键变量的值与程序执行流程，定位代码中的逻辑错误与运行时异常。此外，结合GDB Server或OpenOCD等工具，GDB能够更高效地对嵌入式系统进行远程调试，助力开发者快速解决复杂的软件问题，保障嵌入式程序的稳定性与可靠性。

4. <strong>构建工具</strong>

Makefile作为自动化构建工具，在嵌入式开发项目中扮演着关键角色。它通过定义项目中的源文件、编译规则与依赖关系，实现代码的批量编译与链接。开发者只需编写简洁的Makefile脚本，即可通过make命令自动完成从源文件到可执行文件的整个构建过程。同时，Makefile支持增量编译，仅重新编译修改过的文件，显著缩短项目构建时间，尤其适用于大型嵌入式项目的管理。
