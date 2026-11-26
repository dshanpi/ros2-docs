---
title: "2.2 设置开发工具"
sidebar_label: "2.2 设置开发工具"
slug: /chapter-02/section-02/
---

## 2.2.1 安装和配置VSCodium

如果我们直接在终端上使用vim等类似的编辑工具编写代码，往往会觉得不习惯，而日常编写代码，我们习惯于在PC上借助VSCode或者其他编辑器编写代码。

在这里，我们需要下载VSCodium进行SSH远程登录MUSE-PI-PRO主板。VSCodium进行SSH远程登录时，会在主板上自动下载远程开发的核心组件“.vscodium-server”，从而与MUSE-PI-PRO主板建立连接。

疑问：

为什么不使用VSCode？

答：目前VSCode的远程开发组件还不支持riscv64架构，需要使用开源版本的VSCode。

前面《硬件与软件开发环境》有对应的访问链接。

下载VSCodium的步骤如下：

1. <strong>点击Releases。</strong>

打开链接后，这里会显示可以下载到最新软件包的入口。点击进入。

[![图2.30](/img/manual/image34.png)](/img/manual/image34.png)

*图2.30*

2. <strong>找到对应平台的版本。</strong>

可以看到目前最新的的版本如图2.31所示：

[![图2.31](/img/manual/image35.png)](/img/manual/image35.png)

*图2.31*

选择对应的安装包，这里下载到Windows。下载安装包之后，根据提示安装即可。

## 2.2.2 使用Remote-SSH连接开发板

1. <strong>下载插件</strong>

安装完成后，打开VSCodium，在应用商城中下载两个插件，如图2.32所示：

[![图2.32 下载插件](/img/manual/image36.png)](/img/manual/image36.png)

*图2.32 下载插件*

- Chinese：这个插件用于转换VSCodium语言环境为中文（重启生效）。

- Remote-SSH：用于SSH远程连接MUSE-PI-PRO主板。

2. <strong>添加IP地址与用户名</strong>

接下来我们需要添加主板对应的IP地址，实现VSCodium远程SSH登录主板。具体步骤如图2.33：

[![图2.33 配置SSH](/img/manual/image37.png)](/img/manual/image37.png)

*图2.33 配置SSH*

保存刷新之后，右键对应的Host名，选择当前窗口SSH连接主板或者也可以选择创建新的窗口SSH连接主板。如图2.34所示：

[![图2.34 SSH连接主板](/img/manual/image38.png)](/img/manual/image38.png)

*图2.34 SSH连接主板*

3. <strong>输入密码</strong>

接着需要输入密码，回车确认连接，如图2.35所示：

[![图2.35 输入密码](/img/manual/image39.png)](/img/manual/image39.png)

*图2.35 输入密码*

4. <strong>报错处理</strong>

注：正常情况下，会直接连接成功，如果出现了以下报错，如图2.36所示：

[![图2.36 连接报错](/img/manual/image40.png)](/img/manual/image40.png)

*图2.36 连接报错*

这个报错是因为，主板无法下载远程开发的核心组件“.vscodium-server”，那么我们就需要在Windows手动下载。在前面的下载链接下面找到如下图2.37安装包：

[![图2.37](/img/manual/image41.png)](/img/manual/image41.png)

*图2.37*

通过前面Windows与主板文件传输的方式，把该安装包上传至如下路径并解压再重新进行SSH连接。

[![图2.38](/img/manual/image42.png)](/img/manual/image42.png)

*图2.38*

下面是目前演示的指令，每个版本的ID都不一样，根据实际情况执行指令：

```text
cd ~/.vscodium-server/bin/1f9bbd5db96ffb6200c7732948af7aeb7d0773ae
上传文件
tar -xzf vscodium-reh-linux-riscv64-1.99.32704.tar.gz
```

## 2.2.3 VSCodium远程开发

连接成功之后，可以在VSCodium访问MUSE-PI-PRO主板的终端，点击“终端”-&gt; 选择“新建终端”，如下图所示：

[![图2.39](/img/manual/image43.png)](/img/manual/image43.png)

*图2.39*

也可以打开文件，点击“资源管理器”-&gt; “打开文件夹”，如下图所示：

[![图2.40](/img/manual/image44.png)](/img/manual/image44.png)

*图2.40*

找到需要打开的文件路径，输入密码回车即可打开文件夹。

## 2.2.4 Hello程序及背后知识

接下来编写第一个Hello程序，在任意路径下创建一个hello.c文件，填入以下内容：

```c
#include "stdio.h"

int main()
{
    printf("MUSE-PI-PRO Hello World!\n");
    return 0;
}
```

执行编译、运行：

```bash
gcc hello.c -o hello
./hello
```

输出如下：

```bash
MUSE-PI-PRO Hello World!
```

在这里可以思考几个问题：

1. c文件有什么用？答：定义/实现define。

2. 头文件	有什么用？答：声明declare

3. 头文件在哪里？答：-默认路径：/usr/include；-可指定，编译时用-I选项指定目录。

4. printf函数在哪里？答：-库-&gt;库在哪？（默认路径：/usr/lib/；可指定，编译时用-L选项指定目录，“-l”选项指定库）；-别的c文件。
