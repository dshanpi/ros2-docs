---
title: "3.1 Linux常用指令"
sidebar_label: "3.1 Linux常用指令"
slug: /chapter-03/section-01/
---

## 3.1.1 目录/文件操作命令

1. <strong>p</strong><strong>wd</strong>

[![图2.1 pwd](/img/manual/image45.png)](/img/manual/image45.png)

*图2.1 pwd*

2. <strong>cd</strong>

[![图2.2 cd](/img/manual/image46.png)](/img/manual/image46.png)

*图2.2 cd*

cd命令有些缩略用法：

```bash
$ cd  -   // 进入上次目录, 比如先进入a目录再进入b目录，执行此命令后即回到a目录
$ cd  ~   // 进入家目录
```

3. <strong>mkdir</strong>

[![图2.3 mkdir](/img/manual/image47.png)](/img/manual/image47.png)

*图2.3 mkdir*

4. <strong>rmdir</strong>

[![图2.4 rmdir](/img/manual/image48.png)](/img/manual/image48.png)

*图2.4 rmdir*

5. <strong>ls</strong>

[![图2.5 ls](/img/manual/image49.png)](/img/manual/image49.png)

*图2.5 ls*

使用示例：

[![图2.6 ls/ls -l](/img/manual/image50.png)](/img/manual/image50.png)

*图2.6 ls/ls -l*

[![图2.7 ls -a/ls -la/ls -lh](/img/manual/image51.png)](/img/manual/image51.png)

*图2.7 ls -a/ls -la/ls -lh*

6. <strong>cp</strong>

[![图2.8 cp](/img/manual/image52.png)](/img/manual/image52.png)

*图2.8 cp*

复制目录时，常用如下命令：

```bash
$ cp  -rfd  dir_a  dir_b
```

- <strong>r：recursive，递归地，即复制所有文件</strong>

- <strong>f：force，强制覆盖</strong>

- <strong>d：如果源文件为链接文件，也只是把它作为链接文件复制过去，而不是复制实际文件</strong>

7. <strong>rm</strong>

[![图2.9 rm](/img/manual/image53.png)](/img/manual/image53.png)

*图2.9 rm*

删除目录时，常用如下命令：

```bash
$ rm  -rf  dir_a
```

- <strong>r：recursive，递归地，即删除所有文件</strong>

- <strong>f：force，强制删除</strong>

8. <strong>cat</strong>

[![图2.10 cat](/img/manual/image54.png)](/img/manual/image54.png)

*图2.10 cat*

9. <strong>touch</strong>

[![图2.11 touch](/img/manual/image55.png)](/img/manual/image55.png)

*图2.11 touch*

## 3.1.2 改变文件的权限和属性

- <strong>chgrp：改变文件所属用户组</strong>

- <strong>chown：改变文件所有者</strong>

- <strong>chmod：改变文件的权限</strong>

1. <strong>ch</strong><strong>grp</strong><strong>改变文件所属用户组</strong>

```bash
chgrp 【-R】 dirname/filename  ...
```

- <strong>-R:进行递归的持续更改，也连同子目录下的所有文件、目录都更新成为这个用户组之意。常常用在更改某一目录内所有文件的情况。</strong>

范例：

```bash
chgrp  hy  install.log
```

将install.log文件的用户组改为hy用户组。注意hy用户组必须要在/etc/group 文件内存在才可以。

2. <strong>chowm改变文件的所有者</strong>

```text
chown [-R]  账号名  文件或目录
chown [-R] 账号名:组名  文件或目录
```

- <strong>-R：也是递归子目录。</strong>

<strong>范例：</strong>

```bash
chown bin install.log
chown  book:book  install.log
```

改变文件所有者和用户组的这两个命令的应用场景：复制文件，由于复制行为会复制执行者的属性和权限，因此复制后需要改变文件所属用户、用户组等。

3. <strong>chmod改变文件的权限</strong>

文件权限有两种设置方法：数字类型改变权限和符号改变权限。

首先说明各个权限对应的数字：

- <strong>r:  4或0</strong>

- <strong>w:  2或0</strong>

- <strong>x:  1或0</strong>

<strong>这3种权限的取值相加后，就是权限的数字表示。例如：文件a的权限为“-rwxrwx---”，它的数值表示为：</strong>

- <strong>owner = rwx = 4+2+1 = 7</strong>

- <strong>group = rwx = 4+2+1 = 7</strong>

- <strong>others = --- = 0+0 +0 = 0</strong>

<strong>所以在设置权限时，该文件的权限数字就是770。</strong>

1. <strong>数字类型改变权限</strong>

使用数值改变文件权限的命令如下：

```text
chmod [-R]  xyz  文件或目录
```

- <strong>xyz：代表权限的数值，如770。</strong>

- <strong>-R：以递归方式进行修改，比如修改某个目录下所有文件的属性。</strong>

范例：

```bash
chmod 777 .bashrc 
```

将文件.bashrc这个文件的所有权限设置都启用。

2. <strong>符号类型改变文件权限方式</strong>

使用u、g、o三个字母代表user、group、others 3中身份。此外a代表all，即所有身份。

范例：

```bash
chmod u=rwx,go=rx  .bashrc
```

也可以增加或去除某种权限，“+”表示添加权限，“-”表示去除权限：

```bash
chmod a+w  .bashrc
chmod a-x  .bashrc
```

## 3.1.3 查找/搜索命令

1. <strong>f</strong><strong>ind</strong>

在Windows中搜索文件，一般查找文件需要传入两个条件：

1. <strong>在哪些目录中查找；</strong>

1. <strong>查找的内容；</strong>

在Linux中，查找文件的也需要这两个条件，不同于Windows使用搜索框查找，Linux中使用find命令查找文件。

find命令格式为：

```text
find 目录名 选项 查找条件
```

举例1：

```bash
$ find  /home/book/dira/  -name  " test1.txt " 
```

说明:

- <strong>/home/book/dira/指明了查找的路径。</strong>

- <strong>“-name”表明以名字来查找文件 。</strong>

- <strong>“test1.txt”，就指明查找名为“test1.txt”的文件。</strong>

举例2：

```bash
$ find  /home/book/dira/ -name  " *.txt " 
```

说明:查找指定目录下面所有以“.txt”结尾的文件，其中“\*”是通配符。

举例3：

```bash
find  /home/book/dira/  -name "dira"	
```

说明: 查找指定目录下面是否存在“dira”这个目录或文件，“dira”是名称。

<strong>注意：</strong>

1. <strong>如果没有指定查找目录，则为当前目录。</strong>

```bash
$ find . -name " *.txt "    //其中.代表当前路径。 
$ find -name " *.txt "      //没加路径，默认是当前路径下查找。
```

2. <strong>find还有一些高级的用法，如查找最近几天(几个小时)之内(之前)有变动的文件。</strong>

```bash
$ find  /home/book  -mtime -2       //查找/home目录下两天内有变动的文件。
```

2. <strong>g</strong><strong>rep</strong>

grep命令的作用是查找文件中符合条件的字符串，其格式如下：

```text
grep [选项] [查找模式] [文件名]。
```

假设dira目录的test1.txt和dirb目录的test1.txt都含有如下内容：aaa AAAAAA abc abcabcabc cbacbacba match\_pattern nand-&gt;erase。

通过查找字符串，希望显示如下内容：

1. <strong>所在的文件名----grep查找时默认已经显示目标文件名</strong>

3. <strong>所在的行号------使用-n选项。</strong>

grep -rn "字符串" 文件名 r(recursive)：递归查找 n(number)：显示目标位置的行号

- <strong>字符串:要查找的字符串</strong>

- <strong>文件名:要查找的目标文件，如果是\*则表示查找当前目录下的所有文件和目录。</strong>

举例：

```bash
//在test1.txt中查找字符串abc grep -rn "abc" * 在当前目录递归查找字符串abc
$ grep -n "abc" test1.txt  
```

<strong>注意：可以加入-w全字匹配。</strong>

可以在grep的结果中再次执行grep搜索，比如搜索包含有ABC的头文件，可执行如下命令：

```bash
$ grep  “ABC”  *  -nR  |  grep “\.h”
```

上述命令把第1个命令“grep  “ABC”  \*  -nR”通过管道传给第2个命令。即第2个命令在第1个命令的结果中搜索。

## 3.1.4 压缩/解压命令

1. <strong>g</strong><strong>zip</strong>

gzip的常用选项：

- <strong>-l(list)	    列出压缩文件的内容。</strong>

- <strong>-k(keep)	    在压缩或解压时，保留输入文件。</strong>

- <strong>-d(decompress)	将压缩文件进行解压缩。</strong>

举例：

1. 查看压缩文件

```bash
$ gzip -l  pwd.1.gz
```

2. 解压文件

```bash
$ gzip -kd pwd.1.gz   //该压缩文件是以.gz结尾的单个文件
```

3. 压缩文件

```bash
$ gzip -k mypwd.1    /得到了一个.gz结尾的压缩文件
```

<strong>注意：</strong>

1. <strong>如果gzip不加任何选项，此时为压缩。压缩完该文件会生成后缀为.gz的压缩文件，并删除原来的文件。所以，推荐使用gzip -k来压缩源文件，这样会保留原来的文件。</strong>

2. <strong>相同的文件内容，如果文件名不同，压缩后的大小也不同。</strong>

3. <strong>gzip只能压缩单个文件，不能压缩目录。</strong>

2. <strong>b</strong><strong>zip2</strong>

bzip2的常用选项：

- <strong>-k(keep)	在压缩或解压时，保留输入文件；</strong>

- <strong>-d(decompress)	将压缩文件进行解压缩；</strong>

1. <strong>压缩文件</strong>

```bash
$ bzip2 -k mypwd.1 得到一个.bz2后缀的压缩文。
```

2. <strong>解压文件</strong>

```bash
$ bzip2 -kd mypwd.1.bz2
```

<strong>注意：</strong>

- <strong>如果bzip2不加任何选项，此时为压缩</strong>

- <strong>压缩完该文件会生成后缀为.bz2的压缩文件， 并删除原来的文件。所以说，推荐使用bzip2 -k 来压缩文件，这样可以保留原来的文件。</strong>

- <strong>bzip2只能压缩单个文件，不能压缩目录。</strong>

- <strong>单个文件的压缩使用gzip或bzip2，压缩有两个参数：</strong>

  - <strong>压缩时间</strong>

  - <strong>压缩比。</strong>

一般情况下，小文件使用gzip来压缩，大文件使用bzip2来压缩。bzip2的的压缩率更高。

3. <strong>t</strong><strong>ar</strong>

tar常用选项：

- <strong>-c(create)：表示创建用来生成文件包 。</strong>

- <strong>-x：表示提取，从文件包中提取文件。</strong>

- <strong>-t：可以查看压缩的文件。</strong>

- <strong>-z：使用gzip方式进行处理，它与”c“结合就表示压缩，与”x“结合就表示解压缩。</strong>

- <strong>-j：使用bzip2方式进行处理，它与”c“结合就表示压缩，与”x“结合就表示解压缩。</strong>

- <strong>-v(verbose)：详细报告tar处理的信息。</strong>

- <strong>-f(file)：表示文件，后面接着一个文件名。 -C &lt;指定目录&gt; 解压到指定目录。</strong>

<strong>例1：tar打包、gzip压缩</strong>

1. <strong>把目录dira压缩、打包为dira.tar.gz文件：</strong>

```bash
$ tar czvf dira.tar.gz dira。
```

<strong>注意：</strong>“tar –czvf”与“tar czvf”是一样的效果，所以说，后面统一取消“-”。

2. <strong>查看压缩文件：</strong>

```bash
$ tar tvf  dira.tar.gz
```

3. <strong>解压文件，可以用-C 指定解压到哪个目录：</strong>

```bash
$ tar xzvf dira.tar.gz                 //解压到当前目录 
$ tar xzvf dira.tar.gz -C /home/book   //解压到/home/book。
```

<strong>例2：tar打包、bzip2压缩</strong>

1. <strong>把目录dira压缩、打包为dira.tar.bz2文件</strong>

```bash
$ tar cjvf dira.tar.bz2 dira
```

2. <strong>查看压缩文件</strong>

```bash
$ tar tvf dira.tar.bz2
```

3. <strong>解压文件，可以用-C 指定解压到哪个目录</strong>

```bash
$ tar xjvf dira.tar.bz2                   //解压到当前目录:  
$ tar xjvf dira.tar.bz2 -C /home/book     //解压到/home/book
```

## 3.1.5 网络命令

1. <strong>ifconfig</strong>

- <strong>查看网络、设置IP。ifconfig常用选项：</strong>

- <strong>-a ：显示所有网卡接口</strong>

- <strong>up：激活网卡接口</strong>

- <strong>down：关闭网卡接口</strong>

- <strong>address：xxx.xxx.xxx.xxx，IP地址</strong>

示例：

1. <strong>ifconfig：查看当前正在使用的网卡</strong>

```bash
$ ifconfig
```

[![图2.12](/img/manual/image56.png)](/img/manual/image56.png)

*图2.12*

2. <strong>ifconfig -a：查看所有网卡</strong>

```bash
$ ifconfig -a
```

[![图2.13](/img/manual/image57.png)](/img/manual/image57.png)

*图2.13*

3. <strong>设置网IP：</strong>

```bash
$ sudo ifconfig ens160 192.168.1.137
```

2. <strong>r</strong><strong>oute</strong><strong>和D</strong><strong>NS</strong>

确保Windows和Ubuntu的网络能互相ping通之后，如果Ubuntu无法上网，原因通常有2个：路由没设置好，DNS没设置好。

如果执行以下命令不成功，表示路由没设置好：

```bash
$ ping  8.8.8.8
connect: Network is unreachable
```

如果“ping 8.8.8.8”成功，但是“ping  <a href="https://www.baidu.com">www.baidu.com</a>”不成功，则是DNS没设置好：

```bash
$ ping www.baidu.com
ping: unknown host www.baidu.com
```

DNS的设置比较简单，8.8.8.8是好记好用的DNS服务器，修改Ubuntu中的/etc/resolv.conf文件，内容如下：

```bash
nameserver  8.8.8.8
```

路由信息使用route命令查看，其输出信息可以参考链接：

<a href="https://akaedu.github.io/book/ch36s05.html">https://akaedu.github.io/book/ch36s05.html</a>

摘录如下：

假设某主机上的网络接口配置和路由表如下：

```bash
$ ifconfig
eth0      Link encap:Ethernet  HWaddr 00:0C:29:C2:8D:7E
          inet addr:192.168.10.223  Bcast:192.168.10.255  Mask:255.255.255.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:10 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:100
          RX bytes:0 (0.0 b)  TX bytes:420 (420.0 b)
          Interrupt:10 Base address:0x10a0

eth1      Link encap:Ethernet  HWaddr 00:0C:29:C2:8D:88
          inet addr:192.168.56.136  Bcast:192.168.56.255  Mask:255.255.255.0
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:603 errors:0 dropped:0 overruns:0 frame:0
          TX packets:110 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:100
          RX bytes:55551 (54.2 Kb)  TX bytes:7601 (7.4 Kb)
          Interrupt:9 Base address:0x10c0

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:37 errors:0 dropped:0 overruns:0 frame:0
          TX packets:37 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:3020 (2.9 Kb)  TX bytes:3020 (2.9 Kb)
$ route
Kernel IP routing table
estination     Gateway         Genmask         Flags Metric Ref    Use Iface
192.168.10.0    *               255.255.255.0   U     0      0        0 eth0
192.168.56.0    *               255.255.255.0   U     0      0        0 eth1
127.0.0.0       *               255.0.0.0       U     0      0        0 lo
default         192.168.10.1     0.0.0.0         UG    0      0        0 eth0
```

上述route命令输出信息中各项的含义请看下表：

<table>
<tbody>
<tr>
<th scope="col">Destination</th>
<th scope="col">目标网段或者主机</th>
</tr>
<tr>
<td>Gateway</td>
<td>网关地址，”*” 表示目标是本主机所属的网络，不需要路由</td>
</tr>
<tr>
<td>Genmask</td>
<td>网络掩码</td>
</tr>
<tr>
<td rowspan="8">Flags</td>
<td>标记。一些可能的标记如下：</td>
</tr>
<tr>
<td>U - 路由是活动的</td>
</tr>
<tr>
<td>H - 目标是一个主机</td>
</tr>
<tr>
<td>G - 路由指向网关</td>
</tr>
<tr>
<td>R - 恢复动态路由产生的表项</td>
</tr>
<tr>
<td>D - 由路由的后台程序动态地安装</td>
</tr>
<tr>
<td>M - 由路由的后台程序修改</td>
</tr>
<tr>
<td>! - 拒绝路由</td>
</tr>
<tr>
<td>Metric</td>
<td>路由距离，到达指定网络所需的中转数</td>
</tr>
<tr>
<td>Ref</td>
<td>路由项引用次数</td>
</tr>
<tr>
<td>Use</td>
<td>此路由项被路由软件查找的次数</td>
</tr>
<tr>
<td>Iface</td>
<td>该路由表项对应的输出接口</td>
</tr>
</tbody>
</table>

在上面的例子中，这台主机有两个网络接口：

1. <strong>一个网络接口连到192.168.10.0/24网络</strong>

2. <strong>另一个网络接口连到192.168.56.0/24网络。</strong>

如果要发送的数据包的目的地址是192.168.56.3，跟第一行的子网掩码做与运算得到192.168.56.0，与第一行的目的网络地址不符，再跟第二行的子网掩码做与运算得到192.168.56.0，正是第二行的目的网络地址，因此从eth1接口发送出去，由于192.168.56.0/24正是与eth1接口直接相连的网络，因此可以直接发到目的主机，不需要经路由器转发。

如果要发送的数据包的目的地址是202.10.1.2，跟前三行路由表条目都不匹配，那么就要按缺省路由条目，从eth0接口发出去，首先发往192.168.10.1路由器，再让路由器根据它的路由表决定下一跳地址。

可以使用route命令管理路由。

示例：

1. <strong>添加路由：首先得确定网关IP，假设为192.168.1.1</strong>

```bash
$ sudo  route  add  default  gw  192.168.1.1
$ ping 8.8.8.8   // 验证
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=53 time=19.8 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=53 time=19.8 ms
```

2. <strong>删除路由：</strong>

```bash
$ sudo  route  del  default  gw  192.168.1.1
```

## 3.1.6 vi编辑器的使用

vi是一个命令，也是一个命令行下的编辑器，它有如下功能：

- <strong>打开文件、新建文件、保存文件</strong>

- <strong>光标移动</strong>

- <strong>文本编辑</strong>

- <strong>(多行间\|多列间)复制、粘贴、删除</strong>

- <strong>查找和替换</strong>

很多人不习惯在命令行下编辑文件，实际开发中也不会经常在命令行下编辑文件。但是在Linux系统中对文件做些简单修改时，使用vi命令的效率非常高。并且在很多时候，比如现场调试时，并没有GUI形式的编辑工具，vi是唯一选择。

1. <strong>模式</strong>

vi编辑器有三种模式,各个模式侧重点不一样：

1. <strong>一般模式（光标移动、复制、粘贴、删除）</strong>

2. <strong>编辑模式（编辑文本）</strong>

3. <strong>命令行模式（查找和替换）</strong>

vi编辑器的三种模式间切换如下图所示:

[![图2.14](/img/manual/image58.png)](/img/manual/image58.png)

*图2.14*

<strong>注意：</strong>

- <strong>当不知道处于何种模式时，按ESC键返回到一般模式。</strong>

- <strong>wq(write quit)</strong>

- <strong>i(insert)</strong>

2. <strong>文件的打开/新建/保存</strong>

打开文件、新建文件，命令如下(如果文件存在则打开文件，否则新建文件并打开)：

```bash
$ vi  文件名
```

修改结束之后，输入“:” 进入命令行模式，再输入“wq”保存退出：

```bash
:wq		保存并退出文件
```

<strong>注意：</strong>如果文件不存在，也需要输入“:wq”才可以保存新文件，否则不会新建文件。

在编辑完成时，返回一般模式，方法如下：

1. <strong>输入“:w”则保存文件，如果已经保存文件，输入“:q”则退出文件</strong>

2. <strong>直接输入“:wq”保存并退出</strong>

3. <strong>如果不想保存被修改的内容，则输入“:q!”强制退出。</strong>

这些命令列表如下：

<table>
<tbody>
<tr>
<th scope="col">命令</th>
<th scope="col">描述</th>
</tr>
<tr>
<td>x</td>
<td>保存当前文档并且退出。</td>
</tr>
<tr>
<td>q</td>
<td>退出。</td>
</tr>
<tr>
<td>w</td>
<td>保存文档 。</td>
</tr>
<tr>
<td>q!</td>
<td>退出 vi/vim，不保存文档。</td>
</tr>
</tbody>
</table>

3. <strong>编辑文件</strong>

打开文件后，默认处于“一般模式”，这时可以输入以下字母：

<table>
<tbody>
<tr>
<th scope="col">指令</th>
<th scope="col">描述</th>
</tr>
<tr>
<td>i</td>
<td>在当前光标所在字符的前面，转为编辑模式。</td>
</tr>
<tr>
<td>I</td>
<td>在当前光标所在行的行首转换为编辑模式。</td>
</tr>
<tr>
<td>a</td>
<td>在当前光标所在字符的后面，转为编辑模式。</td>
</tr>
<tr>
<td>A</td>
<td>在光标所在行的行尾，转换为编辑模式。</td>
</tr>
<tr>
<td>o</td>
<td>在当前光标所在行的下方，新建一行，并转为编辑模式。</td>
</tr>
<tr>
<td>O</td>
<td>在当前光标所在行的上方，新建一行，并转为编辑模式。</td>
</tr>
</tbody>
</table>

4. <strong>快速移动光标</strong>

在一般模式下，可以使用下面快捷键移动光标或是翻页：

<table>
<tbody>
<tr>
<th scope="col" colspan="2">移动光标</th>
</tr>
<tr>
<td>h (或左方向键)</td>
<td>光标左移一个字符。</td>
</tr>
<tr>
<td>l (或右方向键)</td>
<td>光标右移一个字符。</td>
</tr>
<tr>
<td>j (或下方向键)</td>
<td>光标下移一行。</td>
</tr>
<tr>
<td>k (或上方向键)</td>
<td>光标上移一行。</td>
</tr>
<tr>
<td>nG或ngg</td>
<td>光标移动到第 n行首。</td>
</tr>
<tr>
<td>n+</td>
<td>光标下移 n行。</td>
</tr>
<tr>
<td>n-</td>
<td>光标上移 n行。</td>
</tr>
<tr>
<td colspan="2">屏幕翻滚</td>
</tr>
<tr>
<td>Ctrl + f</td>
<td>屏幕向下翻一页，相当于下一页。</td>
</tr>
<tr>
<td>Ctrl + b</td>
<td>屏幕向上翻一页，相当于上一页。</td>
</tr>
</tbody>
</table>

详细介绍如下：

1. <strong>快速的定位到某一行：文件头、文件尾、指定某一行</strong>

- <strong>ngg：光标移至第n行的行首（n为数字,想要跳转的行），</strong>

- <strong>1gg：就跳到第一行的行首，就是文件头</strong>

- <strong>2gg：就跳到第二行的行首</strong>

- <strong>G：转至文件结尾</strong>

4. <strong>在某一行如何快速定位到某一列：</strong>

- <strong>0:（数字零）光标移至当前行行首</strong>

- <strong>$：光标移至当前行行末</strong>

- <strong>fx：搜索当前行中下一个出现字母x的地方</strong>

<strong>注意：当你不知道vi当前处于何种模式时，使用esc键返回到一般模式。</strong>

5. <strong>文本复制/粘贴/删除/撤销</strong>

在一般模式下，可以执行以下命令：

<table>
<tbody>
<tr>
<th scope="col" colspan="2">复制、删除和粘贴</th>
</tr>
<tr>
<td>cc</td>
<td>删除整行，并且修改整行内容。</td>
</tr>
<tr>
<td>dd</td>
<td>删除该行，不提供修改功能。</td>
</tr>
<tr>
<td>ndd</td>
<td>删除当前行向下 n行。</td>
</tr>
<tr>
<td>x</td>
<td>删除光标所在的字符。</td>
</tr>
<tr>
<td>X</td>
<td>删除光标前面的一个字符。</td>
</tr>
<tr>
<td>nyy</td>
<td>复制当前行及其下面 n行。</td>
</tr>
<tr>
<td>p</td>
<td>粘贴最近复制的内容。</td>
</tr>
<tr>
<td>s</td>
<td>删除光标所在字符。</td>
</tr>
<tr>
<td>r</td>
<td>替换光标处字符。</td>
</tr>
</tbody>
</table>

1. <strong>复制</strong>

```bash
yy   //复制当前行(y:yank(复制))   
nyy  //复制当前行及其后的n-1行(n是数字)
```

2. <strong>粘贴</strong>

```bash
p  //粘贴(p:paste)
```

3. <strong>删除</strong>

```bash
dd   //删除光标所在行(d:delete)
ndd  //删除当前行及其后的n-1行(n是数字)
x    //删除光标所在位置的字符
```

4. <strong>撤销</strong>

```bash
u  //撤销上一步操作
```

6. <strong>文本查找和替换</strong>

在一般模式下，可以执行以下命令。

1. <strong>查找</strong>

```bash
/pattern  //从光标开始处向文件尾搜索pattern，后按下n或N
```

<strong>注意：</strong>

- <strong>n：在同一个方向重复上一次搜索命令</strong>

- <strong>N：在反方向重复上一次搜索命令</strong>

- <strong>在/pattern之前先跳到第一行则进行全文件搜索。</strong>

2. <strong>替换</strong>

- <strong>:%s/p1/p2/g   //将文件中所有的p1均用p2替换</strong>

- <strong>:%s/p1/p2/gc  //替换时需要确认</strong>

- <strong>“s“ 全称：substitute替换；</strong>

- <strong>“g“ 全称：global全局；</strong>

- <strong>“c“ 全称：confirm，确认</strong>

参考

<a href="https://www.runoob.com/linux/linux-command-manual.html">https://www.runoob.com/linux/linux-command-manual.html</a>

7. <strong>vi编辑器使用示例</strong>

本例创建一个名为hello.txt的文件，添加如下2行文件字，再回退去删除第2行的字母“X”：

```text
www.100ask.net
wiki.100askX.net
```

首先执行以下命令，如果当前目录下没有hello.txt它就会新建并打开该文件，否则直接打开该文件：

```bash
vi  hello.txt
```

界面如下：

[![图2.15](/img/manual/image59.png)](/img/manual/image59.png)

*图2.15*

输入字符“i”，它表示“insert”，即在光标前输入字符，界面如下：

[![图2.16](/img/manual/image60.png)](/img/manual/image60.png)

*图2.16*

在上述界面中，可以输入字符了，可以使用回车键、删除键、箭头键等等，跟一般得文本工具没什么差别，如下：

[![图2.17](/img/manual/image61.png)](/img/manual/image61.png)

*图2.17*

无论当前是否处于编辑模式，都可以使用箭头键移动光标。

- <strong>在编辑模式下，使用删除键(Backspace)删除字符;</strong>

- <strong>不在编辑模式下时，使用“x”删除光标所在的字符;</strong>

[![图2.18](/img/manual/image62.png)](/img/manual/image62.png)

*图2.18*

最后输入“:wq”保存并退出，“:”表示进入命令行模式，“wq”表示“write and quit”，即写入并退出。如果不想保存则可以输入“:q!”，它表示“退出、不保存”:

[![图2.19](/img/manual/image63.png)](/img/manual/image63.png)

*图2.19*

最后执行“cat  hello.txt”命令验证一下：

[![图2.20](/img/manual/image64.png)](/img/manual/image64.png)

*图2.20*

## 3.1.7 其他命令

1. <strong>file</strong>

查看文件类型。其格式如下：

```text
file 文件名
```

2. <strong>w</strong><strong>hich</strong><strong>和w</strong><strong>hereis</strong>

which命令和whereis命令作用是查找命令或应用程序的所在位置，其格式如下：

```text
which   命令名/应用程序名
whereis  命令名/应用程序名。
```

示例：

```bash
$ which pwd     //定位到/bin/pwd
$ which gcc     //定位到/usr/bin/gcc 
$ whereis pwd   //可得到可执行程序的位置和手册页的位置
```
