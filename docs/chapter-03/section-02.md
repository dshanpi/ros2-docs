---
title: "3.2 包管理入门"
sidebar_label: "3.2 包管理入门"
slug: /chapter-03/section-02/
---

## 3.2.1 软件包管理系统

像我们日常使用的windows提供的应用商店或者手机提供的应用市场那样，大多数现代的类 Unix 操作系统也都提供了一种中心化的机制用来搜索和安装软件。软件通常存放在存储库中，并通过包的形式对外进行分发。处理包的工作称为包管理。包提供了操作系统的基本组件，以及共享的库、应用程序、服务和文档。这个我们称为软件包管理系统，其除了安装软件外，它还提供了工具来更新已经安装的包。

大多数软件包系统都是围绕软件包文件的集合构建的。软件包文件通常是一个存档文件，它包含已编译的二进制文件和软件的其他资源，以及安装脚本。软件包文件同时也包含有价值的元数据，包括它们的依赖项，以及安装和运行它们所需的其他软件包的列表。

虽然这些包管理系统的功能和优点大致相同，但打包格式和工具会因平台（不同的Linux发行版）而异，如下表所示：

<table>
<tbody>
<tr>
<th scope="col">操作系统</th>
<th scope="col">格式</th>
<th scope="col">工具</th>
</tr>
<tr>
<td>Debian</td>
<td>.deb</td>
<td>apt, apt-cache, apt-get, dpkg</td>
</tr>
<tr>
<td>Ubuntu</td>
<td>.deb</td>
<td>apt, apt-cache, apt-get, dpkg</td>
</tr>
<tr>
<td>CentOS</td>
<td>.rpm</td>
<td>yum</td>
</tr>
<tr>
<td>Fedora</td>
<td>.rpm</td>
<td>dnf</td>
</tr>
<tr>
<td>FreeBSD</td>
<td>Ports, .txz</td>
<td>make, pkg</td>
</tr>
</tbody>
</table>

由上表可知，Debian 及其衍生版，如我们现在使用的BianbuOS是基于Ubuntu社区源码构建的，它们的包格式为 .deb。APT 这款先进的软件包管理工具提供了大多数常见的命令如：搜索存储库、安装软件包及其依赖项，并管理升级，等等。在系统中，我们还可以使用 dpkg 程序来安装单个的 deb 文件，APT 命令作为底层 dpkg 的前端，有时也会直接调用它。

目前发布的 debian 衍生版大多数都包含了 apt 命令，它提供了一个简洁统一的接口，可用于通常由 apt-get 和 apt-cache 命令处理的常见操作。这个命令是可选的，但使用它可以简化一些任务。

## 3.2.2 apt命令使用

上一小节介绍了软件包管理系统，本小节秉承上小节的内容，介绍软件包管理系统中apt命令。

我们习惯于使用windows系统以及智能手机，这两个下载和安装软件都是非常容易简单的。但是BianbuOS下该如何安装软件呢？BianbuOS安装软件不像Windows下那样，直接双击.exe文件就开始安装了。一般来说BianbuOS下很多软件是需要先自行提供源码，使用源码自行编译，编译完成以后使用命令”install”来安装到系统中。当然 BianbuOS下也有其它的软件安装方法，使用得最多的方法就是自行编译源码后进行安装，尤其是嵌入式 Linux开发。命令 ”install” 格式如下所示：

```text
install [选项 ]... [-T] 源文件 目标文件
install [选项 ]... 源文件 ... 目录
install [选项 ]... -t 目录 源文件 ... 或： install [选项 ]... -d 目录 ...
```

“install” 命令是将文件 (通常是编译后的文件 )复制到目的位置，在上面得三种形式中，将源文件复制到目标文件或将多个源文件复制到一个已存在的目录中同时设置其所有权和权限模式。在第四种形式会创建指定的目录。命令“ install”通常和命令 apt-get”组合在一起使用的。

例如，下载vim工具：

```text
sudo apt-get install vim
```

APT下载工具和上面讲解到的 ”install” 命令结合构成了BianbuOS下最常用的下载和安装软件方法。并且其解决了Linux平台下一安装软件的一个缺陷：即软件之间相互依赖问题。

## 3.2.3 更新BianbuOS软件源

APT采用 C/S 模式，也就是客户端/服务器模式，一般来说我们的MUSE-PI-RRO主板作为客户端，当需要下载软件的时候就向服务器请求，因此我们需要知道服务器的地址，也叫做软件源或者更新源，但在这里我们不修改软件源，使用默认的软件源，也就是进迭时空提供的软件源，适合该主板的架构。如果我们需要修改软件源的内容，可以进行修改以下文件：

<strong>修改配置文件：</strong>

- <strong>首先备份源列表</strong>

```bash
sudo cp /etc/apt/sources.list.d/bianbu.sources /etc/apt/sources.list.d/bianbu.sources_back
```

- <strong>打开sources.list文件，进行修改</strong>

```bash
sudo vim /etc/apt/sources.list.d/bianbu.sources	
```

在我们使用APT工具下载安装或者更新软件的时候，首先会在下载列表中与本机软件进行对比，看一下需要下载哪些软件，或者升级哪些软件，默认情况下 APT会下载并安装最新的软件包，被安装的软件包所依赖的其它软件也会被下载安装或者更新，非常智能省心。
