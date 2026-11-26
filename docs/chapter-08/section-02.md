---
title: "8.2 网络编程主要函数介绍"
sidebar_label: "8.2 网络编程主要函数介绍"
slug: /chapter-08/section-02/
---

## 8.2.1 socket函数

```text
int socket(int domain, int type,int protocol);
```

此函数用于创建一个套接字。

- <strong>domain</strong>是网络程序所在的主机采用的通讯协族(AF\_UNIX和AF\_INET等)。

  - AF\_UNIX只能够用于单一的Unix 系统进程间通信，而AF\_INET是针对Internet的，因而可以允许远程通信使用。

- <strong>type</strong>是网络程序所采用的通讯协议(SOCK\_STREAM,SOCK\_DGRAM等)。

  - SOCK\_STREAM表明用的是TCP 协议，这样会提供按顺序的，可靠，双向，面向连接的比特流。

  - SOCK\_DGRAM 表明用的是UDP协议，这样只会提不可靠，无连接的通信。

- 关于<strong>protocol</strong>，由于指定了type，所以这个地方一般只要用0来代替就可以了。

此函数执行成功时返回文件描述符，失败时返回-1,看errno可知道出错的详细情况。

## 8.2.2 bind函数

```c
int bind(int sockfd, struct sockaddr *my_addr, int addrlen);
```

从函数用于将地址绑定到一个套接字。

- <strong>sockfd</strong>是由socket函数调用返回的文件描述符。

- <strong>my\_addr</strong>是一个指向sockaddr的指针。

- <strong>addrlen</strong>是sockaddr结构的长度。

sockaddr的定义：

```c
struct sockaddr{
unisgned short  as_family;
char sa_data[14];
};
```

不过由于系统的兼容性,我们一般使用另外一个结构(struct sockaddr\_in) 来代替。

sockaddr\_in的定义：

```c
struct sockaddr_in{
unsigned short   sin_family;     
unsigned short     sin_port;
struct in_addr   sin_addr;
unsigned char   sin_zero[8];
}
```

如果使用Internet所以sin\_family一般为AF\_INET。

- sin\_addr设置为INADDR\_ANY表示可以和任何的主机通信。

- sin\_port是要监听的端口号。

- bind将本地的端口同socket返回的文件描述符捆绑在一起.成功是返回0,失败的情况和socket一样。

## 8.2.3 listen函数

```text
int listen(int sockfd,int backlog);
```

此函数宣告服务器可以接受连接请求。

- <strong>sockfd</strong>是bind后的文件描述符。

- <strong>backlog</strong>设置请求排队的最大长度。当有多个客户端程序和服务端相连时，使用这个表示可以介绍的排队长度。

- listen函数将bind的文件描述符变为监听套接字，返回的情况和bind一样。

## 8.2.4 accept函数

```c
int accept(int sockfd, struct sockaddr *addr,int *addrlen);
```

服务器使用此函数获得连接请求，并且建立连接。

- <strong>sockfd</strong>是listen后的文件描述符。

- <strong>addr</strong>，<strong>addrlen</strong>是用来给客户端的程序填写的,服务器端只要传递指针就可以了， bind,listen和accept是服务器端用的函数。

- accept调用时，服务器端的程序会一直阻塞到有一个客户程序发出了连接。 accept成功时返回最后的服务器端的文件描述符，这个时候服务器端可以向该描述符写信息了，失败时返回-1 。

## 8.2.5 connect函数

```c
int connect(int sockfd, struct sockaddr * serv_addr,int addrlen);
```

可以用connect建立一个连接，在connect中所指定的地址是想与之通信的服务器的地址。

- <strong>sockfd</strong>是socket函数返回的文件描述符。

- <strong>serv\_addr</strong>储存了服务器端的连接信息，其中sin\_add是服务端的地址。

- <strong>addrlen</strong>是serv\_addr的长度

- connect函数是客户端用来同服务端连接的.成功时返回0，sockfd是同服务端通讯的文件描述符，失败时返回-1。

## 8.2.6 send函数

```text
ssize_t send(int sockfd, const void *buf, size_t len, int flags);
```

- <strong>sockfd</strong> 指定发送端套接字描述符；

- <strong>buf</strong> 指明一个存放应用程序要发送数据的缓冲区；

- <strong>len</strong> 指明实际要发送的数据的字节数；

- <strong>flags</strong> 一般置0。

- 客户或者服务器应用程序都用send函数来向TCP连接的另一端发送数据

## 8.2.7 recv函数

```text
ssize_t recv(int sockfd, void *buf, size_t len, int flags);
```

- <strong>sockfd</strong> 指定接收端套接字描述符；

- <strong>buf</strong> 指明一个缓冲区，该缓冲区用来存放recv函数接收到的数据；

- <strong>len</strong> 指明buf的长度；

- <strong>flags</strong> 一般置0。

- 客户或者服务器应用程序都用recv函数从TCP连接的另一端接收数据。

## 8.2.8 recvfrom函数

```c
ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags,
                        struct sockaddr *src_addr, socklen_t *addrlen);
```

- <strong>recvfrom</strong>通常用于无连接套接字，因为此函数可以获得发送者的地址。

- <strong>src\_addr</strong> 是一个struct sockaddr类型的变量，该变量保存源机的IP地址及端口号。

- <strong>addrlen</strong> 常置为sizeof （struct sockaddr）。

## 8.2.9 sendto函数

```c
ssize_t sendto(int sockfd, const void *buf, size_t len, int flags,
                      const struct sockaddr *dest_addr, socklen_t addrlen);
```

- sendto和send相似，区别在于sendto允许在无连接的套接字上指定一个目标地址。

- <strong>dest\_addr</strong> 表示目地机的IP地址和端口号信息，

- <strong>addrlen</strong> 常常被赋值为sizeof （struct sockaddr）。

- <strong>sendto</strong> 函数也返回实际发送的数据字节长度或在出现发送错误时返回-1。
