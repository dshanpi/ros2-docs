---
title: "第5章 Makefile的使用"
sidebar_label: "第5章 Makefile的使用"
slug: /chapter-05/
---

在Linux中使用make命令来编译程序，特别是大程序；而make命令所执行的动作依赖于Makefile文件。最简单的Makefile文件如下：

```bash
hello: hello.c
gcc -o hello hello.c
clean:
rm -f  hello
```

将上述4行存为Makefile文件(注意必须以Tab键缩进第2、4行，不能以空格键缩进)，放入hello.c同一目录下，然后直接执行make命令即可编译程序，执行“make clean”即可清除编译出来的结果。

make命令根据文件更新的时间戳来决定哪些文件需要重新编译，这使得可以避免编译已经编译过的、没有变化的程序，可以大大提高编译效率。

要想完整地了解Makefile的规则，请参考《GNU Make 使用手册》，以下仅粗略介绍。

## 本章目录

- [5.1 Makefile的引入及规则](./section-01.md)
- [5.2 Makefile规则](./section-02.md)
- [5.3 Makefile文件里的赋值方法](./section-03.md)
- [5.4 Makefile常用函数](./section-04.md)
