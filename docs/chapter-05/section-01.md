---
title: "5.1 Makefile的引入及规则"
sidebar_label: "5.1 Makefile的引入及规则"
slug: /chapter-05/section-01/
---

## 5.1.1 Makefile规则与示例

### 1 为什么需要Makefile

怎么高效地编译程序？想达到什么样的效果？请参考Visual Studio：修改源文件或头文件，只需要重新编译牵涉到的文件，就可以重新生成APP

### 2 Makefile其实挺简单

一个简单的Makefile文件包含一系列的“规则”，其样式如下：

```makefile
目标(target)…: 依赖(prerequiries)…
<tab>命令(command)
```

如果“依赖文件”比“目标文件”更加新，那么执行“命令”来重新生成“目标文件”。

命令被执行的2个条件：依赖文件比目标文件新，或是 目标文件还没生成。

### 3 先介绍Makefile的2个函数

- <strong>$(foreach var,list,text)</strong>

简单地说，就是 for each var in list, change it to text。

对list中的每一个元素，取出来赋给var，然后把var改为text所描述的形式。

例子：

```makefile
objs := a.o b.o
dep_files := $(foreach  f,  $(objs),  .$(f).d)  // 最终 dep_files := .a.o.d .b.o.d
```

- <strong>$(wildcard pattern)</strong>

pattern所列出的文件是否存在，把存在的文件都列出来。

例子：

```makefile
src_files := $( wildcard  *.c)  // 最终 src_files中列出了当前目录下的所有.c文件
```

### 4 一步一步完善Makefile

1. <strong>第1个Makefile，简单粗暴，效率低：</strong>

```makefile
test : main.c sub.c sub.h
gcc -o test main.c sub.c
```

2. <strong>第2个Makefile，效率高，相似规则太多太啰嗦，不支持检测头文件：</strong>

```makefile
test : main.o sub.o
gcc -o test main.o sub.o

main.o : main.c
gcc -c -o main.o  main.c

sub.o : sub.c
gcc -c -o sub.o  sub.c	

clean:
rm *.o test -f
```

3. <strong>第3个Makefile，效率高，精炼，不支持检测头文件：</strong>

```makefile
test : main.o sub.o
gcc -o test main.o sub.o
%.o : %.c
gcc -c -o $@  $<

clean:
rm *.o test -f
```

4. <strong>第4个Makefile，效率高，精炼，支持检测头文件(但是需要手工添加头文件规则)：</strong>

```makefile
test : main.o sub.o
gcc -o test main.o sub.o

%.o : %.c
gcc -c -o $@  $<

sub.o : sub.h

clean:
rm *.o test -f
```

5. <strong>第5个Makefile，效率高，精炼，支持自动检测头文件：</strong>

```makefile
objs := main.o sub.o

test : $(objs)
	gcc -o test $^


# 需要判断是否存在依赖文件
# .main.o.d .sub.o.d
dep_files := $(foreach f, $(objs), .$(f).d)
dep_files := $(wildcard $(dep_files))

# 把依赖文件包含进来
ifneq ($(dep_files),)
  include $(dep_files)
endif


%.o : %.c
	gcc -Wp,-MD,.$@.d  -c -o $@  $<
	

clean:
	rm *.o test -f

distclean:
	rm  $(dep_files) *.o test -f
```

## 5.1.2 通用Makefile的使用

参考Linux内核的Makefile编写了一个通用的Makefile，它可以用来编译应用程序：

1. <strong>支持多个目录、多层目录、多个文件；</strong>

2. <strong>支持给所有文件设置编译选项；</strong>

3. <strong>支持给某个目录设置编译选项；</strong>

4. <strong>支持给某个文件单独设置编译选项；</strong>

<strong>简单、好用。</strong>

下列目录中就有说明和示例：

sources\\05\_General-Makefile

## 5.1.3 通用Makefile的解析

- <strong>make命令的使用：</strong>

执行make命令时，它会去当前目录下查找名为“Makefile”的文件，并根据它的指示去执行操作，生成第一个目标。

我们可以使用“-f”选项指定文件，不再使用名为“Makefile”的文件，比如：

```bash
make  -f  Makefile.build 
```

我们可以使用“-C”选项指定目录，切换到其他目录里去，比如：

```bash
make -C  a/  -f  Makefile.build 
```

我们可以指定目标，不再默认生成第一个目标：

```bash
make -C  a/  -f  Makefile.build   other_target
```

- <strong>即时变量、延时变量：</strong>

变量的定义语法形式如下：

```makefile
A  =  xxx    // 延时变量
B  ?= xxx    // 延时变量，只有第一次定义时赋值才成功；如果曾定义过，此赋值无效
C  := xxx    // 立即变量
D  += yyy    // 如果D在前面是延时变量，那么现在它还是延时变量；
// 如果D在前面是立即变量，那么现在它还是立即变量
```

在GNU make中对变量的赋值有两种方式：延时变量、立即变量。上面语句中，变量A是延时变量，它的值在使用时才展开、才确定。比如：

```makefile
A  =  $@
test:
	@echo $A
```

上述Makefile中，变量A的值在执行时才确定，它等于test，是延时变量。如果使用“A := $@”，这是立即变量，这时$@为空，所以A的值就是空。

- <strong>变量的导出(export)：</strong>

在编译程序时，我们会不断地使用“make -C dir”切换到其他目录，执行其他目录里的Makefile。如果想让某个变量的值在所有目录中都可见，要把它export出来。

比如“CC = $(CROSS\_COMPILE)gcc”，这个CC变量表示编译器，在整个过程中都是一样的。定义它之后，要使用“export CC”把它导出来。

- <strong>Makefile中可以使用shell命令：</strong>

比如：

```makefile
TOPDIR := $(shell pwd)
```

这是个立即变量，TOPDIR等于shell命令pwd的结果。

- <strong>在Makefile中怎么放置第1个目标：</strong>

执行make命令时如果不指定目标，那么它默认是去生成第1个目标。

所以“第1个目标”，位置很重要。有时候不太方便把第1个目标完整地放在文件前面，这时可以在文件的前面直接放置目标，在后面再完善它的依赖与命令。比如：

```makefile
First_target:   // 这句话放在前面
．．．．        // 其他代码，比如include其他文件得到后面的xxx变量
First_target : $(xxx)   $(yyy)   // 在文件的后面再来完善
	command
```

- <strong>假想目标：</strong>

我们的Makefile中有这样的目标：

```makefile
clean:
	rm -f $(shell find -name "*.o")
	rm -f $(TARGET)
```

如果当前目录下恰好有名为“clean”的文件，那么执行“make clean”时它就不会执行那些删除命令。这时我们需要把“clean”这个目标，设置为“假想目标”，这样可以确保执行“make clean”时那些删除命令肯定可以得到执行。

使用下面的语句把“clean”设置为假想目标：

```text
.PHONY : clean
```

- <strong>常用的函数：</strong>

1. <strong>$(foreach var,list,text)</strong>

简单地说，就是for each var in list, change it to text。对list中的每一个元素，取出来赋给var，然后把var改为text所描述的形式。

例子：

```makefile
objs := a.o b.o
dep_files := $(foreach  f,  $(objs),  .$(f).d)  // 最终 dep_files := .a.o.d .b.o.d
```

2. <strong>$(wildcard pattern)</strong>

pattern所列出的文件是否存在，把存在的文件都列出来。

例子：

```makefile
src_files := $( wildcard  *.c)  // 最终 src_files中列出了当前目录下的所有.c文件
```

3. <strong>$(filter pattern...,text)</strong>

把text中符合pattern格式的内容，filter(过滤)出来、留下来。

例子：

```makefile
obj-y := a.o b.o c/ d/
DIR :=  $(filter  %/,  $(obj-y))   //结果为：c/ d/
```

4. <strong>$(filter-out pattern...,text)</strong>

把text中符合pattern格式的内容，filter-out(过滤)出来、扔掉。

例子：

```makefile
obj-y := a.o b.o c/ d/
DIR :=  $(filter-out  %/,  $(obj-y))   //结果为：a.o  b.o
```

5. <strong>$(patsubst pattern,replacement,text)</strong>

寻找\`text’中符合格式\`pattern’的字，用\`replacement’替换它们。\`pattern’和\`replacement’中可以使用通配符。

比如：

```makefile
subdir-y    :=  c/  d/
subdir-y	:= $(patsubst  %/,  %,  $(subdir-y))   // 结果为：c  d
```

## 5.1.4 通用Makefile的设计思想

- <strong>在Makefile文件中确定要编译的文件、目录，比如：</strong>

```text
obj-y += main.o
obj-y += a/
```

“Makefile”文件总是被“Makefile.build”包含的。

- <strong>在Makefile.build中设置编译规则，有3条编译规则：</strong>

1. <strong>怎么编译子目录？ 进入子目录编译：</strong>

```text
$(subdir-y):
	make -C $@ -f $(TOPDIR)/Makefile.build
```

2. <strong>怎么编译当前目录中的文件？</strong>

```text
%.o : %.c
	$(CC) $(CFLAGS) $(EXTRA_CFLAGS) $(CFLAGS_$@) -Wp,-MD,$(dep_file) -c -o $@ $<
```

3. <strong>当前目录下的.o和子目录下的built-in.o要打包起来：</strong>

```makefile
built-in.o : $(cur_objs) $(subdir_objs)
	$(LD) -r -o $@ $^
```

- <strong>顶层Makefile中把顶层目录的built-in.o链接成APP：</strong>

```text
$(TARGET) : built-in.o
	$(CC) $(LDFLAGS) -o $(TARGET) built-in.o
```

- <strong>情景演绎</strong>

[![图 3.1 Makefile情景演绎](/img/manual/image70.png)](/img/manual/image70.png)

*图 3.1 Makefile情景演绎*
