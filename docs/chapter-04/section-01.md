---
title: "4.1 GCC编译过程(精简版)"
sidebar_label: "4.1 GCC编译过程(精简版)"
slug: /chapter-04/section-01/
---

一个C/C++文件要经过预处理(preprocessing)、编译(compilation)、汇编(assembly)和链接(linking)等4步才能变成可执行文件。

[![图3.1 编译过程](/img/manual/image68.png)](/img/manual/image68.png)

*图3.1 编译过程*

通过不同的gcc选项可以控制这些过程：

[![图3.2 gcc选项过程说明](/img/manual/image69.png)](/img/manual/image69.png)

*图3.2 gcc选项过程说明*

在日常交流中通常使用“编译”统称这4个步骤，如果不是特指这4个步骤中的某一个，本教程也依惯例使用“编译”这个统称。

gcc使用示例：

```bash
gcc hello.c                    // 输出一个名为a.out的可执行程序，然后可以执行./a.out
gcc -o hello hello.c          // 输出名为hello的可执行程序，然后可以执行./hello
gcc -o hello hello.c -static // 静态链接
gcc -c -o hello.o hello.c    // 先编译(不链接)
gcc -o hello hello.o       // 再链接
```

执行“gcc -o hello hello.c -v”时，可以查看到这些步骤：

```bash
cc1 main.c -o /tmp/ccXCx1YG.s
as         -o /tmp/ccZfdaDo.o /tmp/ccXCx1YG.s
 
cc1 sub.c -o /tmp/ccXCx1YG.s
as         -o /tmp/ccn8Cjq6.o /tmp/ccXCx1YG.s
 
collect2 -o test /tmp/ccZfdaDo.o /tmp/ccn8Cjq6.o ....
```

可以手工执行以下命令体验一下：

```bash
gcc -E -o hello.i hello.c
gcc -S -o hello.s hello.i
gcc -c -o hello.o hello.s
gcc -o hello hello.o
```

## 4.1.1 常用编译选项

在学习时，我们暂时只需要了解表3-1中的选项：

*表 21 GCC常用编译选项*

<table>
<tbody>
<tr>
<th scope="col"><strong>常用选项</strong></th>
<th scope="col"><strong>描述</strong></th>
</tr>
<tr>
<td><strong>-</strong><strong>E</strong></td>
<td>预处理，开发过程中想快速确定某个宏可以使用“-E  -dM”</td>
</tr>
<tr>
<td><strong>-</strong><strong>c</strong></td>
<td>把预处理、编译、汇编都做了，但是不链接</td>
</tr>
<tr>
<td><strong>-</strong><strong>o</strong></td>
<td>指定输出文件</td>
</tr>
<tr>
<td><strong>-</strong><strong>I</strong></td>
<td>指定头文件目录</td>
</tr>
<tr>
<td><strong>-</strong><strong>L</strong></td>
<td>指定链接时库文件目录</td>
</tr>
<tr>
<td><strong>-</strong><strong>l</strong></td>
<td>指定链接哪一个库文件</td>
</tr>
</tbody>
</table>

## 4.1.2 怎么编译多个文件

1. <strong>一起编译、链接：</strong>

```bash
gcc  -o test  main.c  sub.c
```

2. <strong>分开编译，统一链接：</strong>

```bash
gcc -c -o main.o  main.c
gcc -c -o sub.o   sub.c
gcc -o test main.o sub.o
```

## 4.1.3 制作、使用动态库

1. <strong>制作、编译：</strong>

```bash
gcc -c -o main.o  main.c
gcc -c -o sub.o   sub.c
gcc -shared  -o libsub.so  sub.o  sub2.o  sub3.o(可以使用多个.o生成动态库)
gcc -o test main.o  -lsub  -L /libsub.so/所在目录/
```

1. <strong>运行：</strong>

<strong>先把libsub.so放到/lib目录，然后就可以运行test程序。</strong>

<strong>如果不想把libsub.so放到/lib，也可以放在某个目录比如/a，然后如下执行：</strong>

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/a  
./test
```

## 4.1.4 制作、使用静态库

```bash
gcc -c -o main.o  main.c
gcc -c -o sub.o   sub.c
ar  crs  libsub.a  sub.o  sub2.o sub3.o (可以使用多个.o生成静态库)
gcc  -o  test  main.o  libsub.a  (如果.a不在当前目录下，需要指定它的绝对或相对路径)
```

## 4.1.5 很有用的选项

```bash
gcc -E main.c   // 查看预处理结果，比如头文件是哪个
gcc -E -dM main.c  > 1.txt  // 把所有的宏展开，存在1.txt里
gcc -Wp,-MD,abc.dep -c -o main.o main.c  // 生成依赖文件abc.dep，后面Makefile会用
echo 'main(){}'| gcc -E -v -  // 它会列出头文件目录、库目录(LIBRARY_PATH)
```
