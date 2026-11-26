---
title: "5.3 Makefile文件里的赋值方法"
sidebar_label: "5.3 Makefile文件里的赋值方法"
slug: /chapter-05/section-03/
---

变量的定义语法形式如下：

```makefile
immediate = deferred
immediate ?= deferred
immediate := immediate
immediate += deferred or immediate
define immediate
deferred
endef
```

在GNU make中对变量的赋值有两种方式：延时变量、立即变量。区别在于它们的定义方式和扩展时的方式不同，前者在这个变量使用时才扩展开，意即当真正使用时这个变量的值才确定；后者在定义时它的值就已经确定了。使用\`=’，\`?=’定义或使用define指令定义的变量是延时变量；使用\`:=’定义的变量是立即变量。需要注意的一点是，\`?=’仅仅在变量还没有定义的情况下有效，即\`?=’被用来定义第一次出现的延时变量。

对于附加操作符\`+=’，右边变量如果在前面使用（:=）定义为立即变量则它也是立即变量，否则均为延时变量。
