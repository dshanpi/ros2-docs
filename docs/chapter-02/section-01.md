---
title: "2.1 配置开发环境"
sidebar_label: "2.1 配置开发环境"
slug: /chapter-02/section-01/
---

## 2.1.1 安装必要的必要开发工具

默认系统镜像已经安装了gcc、make和git。可以执行以下指令，查看这几个工具的版本：

```text
gcc -v
git -v
make -v
```

如果工具存在，会出现以下信息：

```text
user@spacemit-k1-x-MUSE-Pi-Pro-board:~$ gcc -v
Using built-in specs.
COLLECT_GCC=gcc
COLLECT_LTO_WRAPPER=/usr/libexec/gcc/riscv64-linux-gnu/13/lto-wrapper
Target: riscv64-linux-gnu
Configured with: ../src/configure -v --with-pkgversion='Bianbu 13.2.0-23ubuntu4bb3' --with-bugurl=file:///usr/share/doc/gcc-13/README.Bugs --enable-languages=c,ada,c++,go,d,fortran,objc,obj-c++,m2 --prefix=/usr --with-gcc-major-version-only --program-suffix=-13 --program-prefix=riscv64-linux-gnu- --enable-shared --enable-linker-build-id --libexecdir=/usr/libexec --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-libstdcxx-backtrace --enable-gnu-unique-object --disable-libitm --disable-libquadmath --disable-libquadmath-support --enable-plugin --with-system-zlib --enable-libphobos-checking=release --with-target-system-zlib=auto --enable-objc-gc=auto --enable-multiarch --disable-werror --disable-multilib --with-tune=spacemit-x60 --with-arch=rv64gc_zba_zbb_zbc_zbs_zicbom_zicbop_zicboz_zicond_zfh_zfhmin --with-abi=lp64d --enable-checking=release --build=riscv64-linux-gnu --host=riscv64-linux-gnu --target=riscv64-linux-gnu
Thread model: posix
Supported LTO compression algorithms: zlib zstd
gcc version 13.2.0 (Bianbu 13.2.0-23ubuntu4bb3)
user@spacemit-k1-x-MUSE-Pi-Pro-board:~$ make -v
GNU Make 4.3
Built for riscv64-unknown-linux-gnu
Copyright (C) 1988-2020 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
user@spacemit-k1-x-MUSE-Pi-Pro-board:~$ git -v
git version 2.43.0
```

如果这些工具没有安装，可以执行以下指令：

```text
sudo apt update
sudo apt install build-essential git
```

这个命令会安装 git 以及 build-essential 包（包含 gcc, make 等）。

## 2.1.2 SSH远程登录与文件传输

前面使用MobaXterm实现了串口登录MUSE-PI-PRO，接下来我们可以在MobaXterm上实现SSH远程登录MUSE-PI-PRO主板。

1. <strong>WiFi联网获取IP地址</strong>

在这之前（如果前面登录系统时连接了WiFi这里可以跳过），需要主板获取IP地址，IP地址可以通过有线或者无线的方式获取，有线获取IP方式只需要接入网线即可自动获取IP（注：需要与PC主机在同一局域网），这里不讲。接下来讲解如何连接WiFi（注：与主机同一个WiFi）。

1. <strong>点击桌面右上角WiFi图标。如图2.21所示：</strong>

[![图2.21 点击WiFi](/img/manual/image25.png)](/img/manual/image25.png)

*图2.21 点击WiFi*

2. <strong>选择可以的WiFi节点，并输入密码。如图2.22所示：</strong>

[![图2.22 输入密码连接WiFi](/img/manual/image26.png)](/img/manual/image26.png)

*图2.22 输入密码连接WiFi*

3. <strong>查看IP地址。</strong>

在终端中输入“ifconfig”，即可查看IP地址，如图2.23所示：

[![图2.23 查看IP地址](/img/manual/image27.png)](/img/manual/image27.png)

*图2.23 查看IP地址*

2. <strong>MobaXterm配置SSH</strong>

获取到ip地址之后，打开 MobaXterm终端工具，参考下图2.24进行配置：

[![图2.24 MobaXterm配置SSH](/img/manual/image28.png)](/img/manual/image28.png)

*图2.24 MobaXterm配置SSH*

1. <strong>点击Session；</strong>

2. <strong>在弹框中找到SSH；</strong>

3. <strong>输入前面查看到的主板IP地址；</strong>

4. <strong>输入创建的用户名user；</strong>

5. <strong>确认。</strong>

确认之后，需要在终端上输入用户名的密码user，然后回车。如图2.25所示：

[![图2.25 输入密码](/img/manual/image29.png)](/img/manual/image29.png)

*图2.25 输入密码*

3. <strong>SSH文件传输</strong>

回车之后，会进入SSH终端界面，如下图2.26所示：

[![图2.26 SSH终端界面](/img/manual/image30.png)](/img/manual/image30.png)

*图2.26 SSH终端界面*

在SSH终端界面左下角可以看到一个选项“Follow terminal folder”，该选项的作用是让左侧的目录树与终端中当前所处的目录保持同步更新。

[![图2.27 勾上Follow terminal folder](/img/manual/image31.png)](/img/manual/image31.png)

*图2.27 勾上Follow terminal folder*

这样我们可以更加方便实现文件传输的位置。在右上角可以看到实现Windows和MUSE\_PI\_PRO主板之间SSH文件传输的图标，如图2.28和图2.29所示：

[![图2.28 Windows上传文件至主板](/img/manual/image32.png)](/img/manual/image32.png)

*图2.28 Windows上传文件至主板*

[![图2.29 主板传输文件至Windows](/img/manual/image33.png)](/img/manual/image33.png)

*图2.29 主板传输文件至Windows*
