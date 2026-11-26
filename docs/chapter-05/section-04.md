---
title: "5.4 Makefile常用函数"
sidebar_label: "5.4 Makefile常用函数"
slug: /chapter-05/section-04/
---

函数调用的格式如下：

```text
$(function arguments)
```

这里\`function’是函数名，\`arguments’是该函数的参数。参数和函数名之间是用空格或Tab隔开，如果有多个参数，它们之间用逗号隔开。这些空格和逗号不是参数值的一部分。内核的Makefile中用到大量的函数，现在介绍一些常用的。

## 5.4.1 字符串替换和分析函数

### 1 $(subst from,to,text)

在文本\`text’中使用\`to’替换每一处\`from’。

比如：$(subst ee,EE,feet on the street)

结果为‘fEEt on the strEEt’。

### 2 $(patsubst pattern,replacement,text)

寻找\`text’中符合格式\`pattern’的字，用\`replacement’替换它们。\`pattern’和\`replacement’中可以使用通配符。

比如：$(patsubst %.c,%.o,x.c.c bar.c)

结果为：\`x.c.o bar.o’。

### 3 $(strip string)

去掉前导和结尾空格，并将中间的多个空格压缩为单个空格。

比如：$(strip a   b c )

结果为\`a b c’。

### 4 $(findstring find,in)

在字符串\`in’中搜寻\`find’，如果找到，则返回值是\`find’，否则返回值为空。

比如：

```bash
$(findstring a,a b c)
$(findstring a,b c)
```

将分别产生值\`a’和\`’(空字符串)。

### 5 $(filter pattern...,text)

返回在\`text’中由空格隔开且匹配格式\`pattern...’的字，去除不符合格式\`pattern...’的字。

比如：$(filter %.c %.s,foo.c bar.c baz.s ugh.h)

结果为\`foo.c bar.c baz.s’。

### 6 $(filter-out pattern...,text)

返回在\`text’中由空格隔开且不匹配格式\`pattern...’的字，去除符合格式\`pattern...’的字。它是函数filter的反函数。

比如：$(filter %.c %.s,foo.c bar.c baz.s ugh.h)

结果为\`ugh.h’。

### 7 $(sort list)

将‘list’中的字按字母顺序排序，并去掉重复的字。输出由单个空格隔开的字的列表。

比如：$(sort foo bar lose)

返回值是‘bar foo lose’。

## 5.4.2 文件名函数

### 1 $(dir names...)

抽取‘names...’中每一个文件名的路径部分，文件名的路径部分包括从文件名的首字符到最后一个斜杠(含斜杠)之前的一切字符。

比如：$(dir src/foo.c hacks)

结果为‘src/ ./’。

### 2 $(notdir names...)

抽取‘names...’中每一个文件名中除路径部分外一切字符（真正的文件名）。

比如：$(notdir src/foo.c hacks)

结果为‘foo.c hacks’。

### 3 $(suffix names...)

抽取‘names...’中每一个文件名的后缀。

比如：$(suffix src/foo.c src-1.0/bar.c hacks)

结果为‘.c .c’。

### 4 $(basename names...)

抽取‘names...’中每一个文件名中除后缀外一切字符。

比如：$(basename src/foo.c src-1.0/bar hacks)

结果为‘src/foo src-1.0/bar hacks’。

### 5 $(addsuffix suffix,names...)

参数‘names...’是一系列的文件名，文件名之间用空格隔开；suffix是一个后缀名。将suffix(后缀)的值附加在每一个独立文件名的后面，完成后将文件名串联起来，它们之间用单个空格隔开。

比如：$(addsuffix .c,foo bar)

结果为‘foo.c bar.c’。

### 6 $(addprefix prefix,names...)

参数‘names’是一系列的文件名，文件名之间用空格隔开；prefix是一个前缀名。将preffix(前缀)的值附加在每一个独立文件名的前面，完成后将文件名串联起来，它们之间用单个空格隔开。

比如：$(addprefix src/,foo bar)

结果为‘src/foo src/bar’。

### 7 $(wildcard pattern)

参数‘pattern’是一个文件名格式，包含有通配符(通配符和shell中的用法一样)。函数wildcard的结果是一列和格式匹配的且真实存在的文件的名称，文件名之间用一个空格隔开。

比如若当前目录下有文件1.c、2.c、1.h、2.h，则：

```makefile
c_src := $(wildcard *.c)
```

结果为‘1.c 2.c’。

## 5.4.3 其他函数

### 1 $(foreach var,list,text)

前两个参数，‘var’和‘list’将首先扩展，注意最后一个参数‘text’此时不扩展；接着，‘list’扩展所得的每个字，都赋给‘var’变量；然后‘text’引用该变量进行扩展，因此‘text’每次扩展都不相同。

函数的结果是由空格隔开的‘text’ 在‘list’中多次扩展后，得到的新‘list’，就是说：‘text’多次扩展的字串联起来，字与字之间由空格隔开，如此就产生了函数foreach的返回值。

下面是一个简单的例子，将变量‘files’的值设置为 ‘dirs’中的所有目录下的所有文件的列表：

```makefile
dirs := a b c d
files := $(foreach dir,$(dirs),$(wildcard $(dir)/*))
```

这里‘text’是‘$(wildcard $(dir)/\*)’，它的扩展过程如下：

1. <strong>第一个赋给变量dir的值是\`a’，扩展结果为‘$(wildcard a/\*)’；</strong>

2. <strong>第二个赋给变量dir的值是\`b’，扩展结果为‘$(wildcard b/\*)’；</strong>

3. <strong>第三个赋给变量dir的值是\`c’，扩展结果为‘$(wildcard c/\*)’；</strong>

<strong>如此继续扩展。</strong>

这个例子和下面的例有共同的结果：

```makefile
files := $(wildcard a/* b/* c/* d/*)
```

### 2 $(if condition,then-part\[,else-part\])

首先把第一个参数‘condition’的前导空格、结尾空格去掉，然后扩展。如果扩展为非空字符串，则条件‘condition’为‘真’；如果扩展为空字符串，则条件‘condition’为‘假’。

如果条件‘condition’为‘真’,那么计算第二个参数‘then-part’的值，并将该值作为整个函数if的值。

如果条件‘condition’为‘假’,并且第三个参数存在，则计算第三个参数‘else-part’的值，并将该值作为整个函数if的值；如果第三个参数不存在，函数if将什么也不计算，返回空值。

<strong>注意：</strong>仅能计算‘then-part’和‘else-part’二者之一，不能同时计算。这样有可能产生副作用（例如函数shell的调用）。

### 3 $(origin variable)

变量‘variable’是一个查询变量的名称，不是对该变量的引用。所以，不能采用‘$’和圆括号的格式书写该变量，当然，如果需要使用非常量的文件名，可以在文件名中使用变量引用。

函数origin的结果是一个字符串，该字符串变量是这样定义的：

```text
‘undefined'				：如果变量‘variable’从没有定义；
‘default'				：变量‘variable’是缺省定义；
‘environment'			：变量‘variable’作为环境变量定义，选项‘-e’没有打开；
‘environment override'	：变量‘variable’作为环境变量定义，选项‘-e’已打开；
‘file' 					：变量‘variable’在Makefile中定义；
‘command line' 			：变量‘variable’在命令行中定义；
‘override' 				：变量‘variable’在Makefile中用override指令定义；
‘automatic' 			：变量‘variable’是自动变量
```

### 4 $(shell command arguments)

函数shell是make与外部环境的通讯工具。函数shell的执行结果和在控制台上执行‘command arguments’的结果相似。不过如果‘command arguments’的结果含有换行符（和回车符），则在函数shell的返回结果中将把它们处理为单个空格，若返回结果最后是换行符（和回车符）则被去掉。

比如当前目录下有文件1.c、2.c、1.h、2.h，则：

```makefile
c_src := $(shell ls *.c)
```

结果为‘1.c 2.c’。

《Makefile介绍》这小节可以在阅读内核、bootloader、应用程序的Makefile文件时，作为手册来查询。下面以options程序的Makefile作为例子进行演示，Makefile的内容如下：

```makefile
File: Makefile
01 src  := $(shell ls *.c)
02 objs := $(patsubst %.c,%.o,$(src))
03 
04 test: $(objs)
05 		gcc -o $@ $^
06
07 %.o:%.c
08		gcc -c -o $@ $<
09 
10 clean:
11		rm -f test *.o		
```

上述Makefile中$@、$^、$&lt;称为自动变量。$@表示规则的目标文件名；$^表示所有依赖的名字，名字之间用空格隔开；$&lt;表示第一个依赖的文件名。‘%’是通配符，它和一个字符串中任意个数的字符相匹配。

options目录下所有的文件为main.c，Makefile，sub.c和sub.h，下面一行行地分析：

1. <strong>第1行src变量的值为‘main.c sub.c’。</strong>

2. <strong>第2行objs变量的值为‘main.o sub.o’，是src变量经过patsubst函数处理后得到的。</strong>

3. <strong>第4行实际上就是：</strong>

```makefile
test : main.o sub.o
```

目标test的依赖有二：main.o和sub.o。开始时这两个文件还没有生成，在执行生成test的命令之前先将main.o、sub.o作为目标查找到合适的规则，以生成main.o、sub.o。

<strong>第7、8行就是用来生成main.o、sub.o的规则：</strong>

对于main.o这个规则就是：

```makefile
main.o:main.c
	gcc -c -o main.o main.c
```

对于sub.o这个规则就是：

```makefile
sub.o:sub.c
	gcc -c -o sub.o sub.c
```

这样，test的依赖main.o和sub.o就生成了。

<strong>第5行的命令在生成main.o、sub.o后得以执行。</strong>

在options目录下第一次执行make命令可以看到如下信息：

```text
gcc -c -o main.o main.c
gcc -c -o sub.o sub.c
gcc -o test main.o sub.o
```

然后修改sub.c文件，再次执行make命令，可以看到如下信息：

```text
gcc -c -o sub.o sub.c
gcc -o test main.o sub.o
```

可见，只编译了更新过的sub.c文件，对main.c文件不用再次编译，节省了编译的时间。
