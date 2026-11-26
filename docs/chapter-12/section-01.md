---
title: "12.1 本地编译内核"
sidebar_label: "12.1 本地编译内核"
slug: /chapter-12/section-01/
---

## 12.1.1 获取内核源码

后面学习驱动基础知识学习需要依赖内核源码，并且将会在本地编译内核源码，不涉及交叉编译，所以只需在MUSE-PI-PRO主板上获取内核源码即可。进入终端，执行以下命令下载内核源码：

```bash
git clone -b k1-bl-v2.2.y --single-branch https://gitee.com/bianbu-linux/linux-6.6.git ~/linux-6.6
```

等待一段时间，如果获取成功，会出现以下信息：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~$ git clone https://gitee.com/bianbu-linux/linux-6.6 ~/linux-6.6
Cloning into '/home/user/linux-6.6'...
remote: Enumerating objects: 9828941, done.
remote: Counting objects: 100% (1820/1820), done.
remote: Compressing objects: 100% (992/992), done.
remote: Total 9828941 (delta 866), reused 1132 (delta 826), pack-reused 9827121 (from 1)
Receiving objects: 100% (9828941/9828941), 2.47 GiB | 6.99 MiB/s, done.
Resolving deltas: 100% (8116519/8116519), done.
Checking objects: 100% (33554432/33554432), done.
Updating files: 100% (85411/85411), done.
```

进入内核源码路径，可以看到如下文件：

[![图 12.1](/img/manual/image122.png)](/img/manual/image122.png)

*图 12.1*

## 12.1.2 安装依赖

在编译内核时，需要用到其他的一些工具，所以在这之前我们需要执行以下指令，下载并安装对应的依赖：

```bash
sudo apt-get update
sudo apt-get install flex bison libncurses-dev debhelper libssl-dev u-boot-tools libpfm4-dev libtraceevent-dev asciidoc bc rsync libelf-dev devscripts -y
```

等待一段时间，即可安装完成。

[![图 12.2](/img/manual/image123.png)](/img/manual/image123.png)

*图 12.2*

## 12.1.3 编译内核

安装依赖后，我们就可以进行编译内核了，具体步骤如下：

① 进入内核源码目录：

```bash
cd ~/linux-6.6
```

② 设置内核编译参数：

```bash
export ARCH=riscv
export LOCALVERSION=""
```

③ 生成默认配置：

```bash
make k1_defconfig
```

④ 编译debian软件包：

```bash
make -j$(nproc) bindeb-pkg
```

当看到以下信息，说明编译成功。

[![图 12.3](/img/manual/image124.png)](/img/manual/image124.png)

*图 12.3*
