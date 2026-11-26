---
title: "8.4 UDP编程"
sidebar_label: "8.4 UDP编程"
slug: /chapter-08/section-04/
---

本节源码位于如下目录：

sources\\08\_socket\\02\_udp\\

client.c源码如下：

```c
#include <sys/types.h>
#include <sys/socket.h>
#include <string.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdio.h>

#define SERVER_PORT 8888

typedef struct UDPClient {
    int fd;
    struct sockaddr_in server_addr;
    char send_buf[1000];
    
    int (*init)(struct UDPClient *p);
    int (*setup)(struct UDPClient *p, const char *ip);
    int (*send_data)(struct UDPClient *p);
    void (*close)(struct UDPClient *p);
} UDPClient;

int init_socket(struct UDPClient *p) {
    p->fd = socket(AF_INET, SOCK_DGRAM, 0);
    return p->fd == -1 ? -1 : 0;
}

int setup_server(struct UDPClient *p, const char *ip) {
    p->server_addr.sin_family = AF_INET;
    p->server_addr.sin_port = htons(SERVER_PORT);
    if (0 == inet_aton(ip, &p->server_addr.sin_addr)) {
        return -1;
    }
    memset(p->server_addr.sin_zero, 0, 8);
    return 0;
}

int send_to_server(struct UDPClient *p) {
    int addr_len = sizeof(struct sockaddr);
    int send_len = sendto(p->fd, p->send_buf, strlen(p->send_buf), 0,
                         (const struct sockaddr *)&p->server_addr, addr_len);
    return send_len <= 0 ? -1 : 0;
}

void close_socket(struct UDPClient *p) {
    close(p->fd);
}

int main(int argc, char **argv)
{
	if (argc != 2)
	{
		printf("Usage:\n");
		printf("%s <server_ip>\n", argv[0]);
		return -1;
	}

	UDPClient client = {
		.init = init_socket,
		.setup = setup_server,
		.send_data = send_to_server,
		.close = close_socket
	};

	if ((*(client.init))(&client) == -1) {
		printf("socket init failed\n");
		return -1;
	}

	if ((*(client.setup))(&client, argv[1]) == -1) {
		printf("invalid server_ip\n");
		(*(client.close))(&client);
		return -1;
	}

	printf("Ready to send messages. Type and press enter:\n");
	while (1)
	{
		if (fgets(client.send_buf, sizeof(client.send_buf), stdin))
		{
			if ((*(client.send_data))(&client) == -1) {
				(*(client.close))(&client);
				return -1;
			}
		}
	}
	
	(*(client.close))(&client);
	return 0;
}
```

server.c源码如下：

```c
#include <sys/types.h>          /* See NOTES */
#include <sys/socket.h>
#include <string.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

#define SERVER_PORT 8888

typedef struct UDPServer {
    int socket_fd;
    struct sockaddr_in server_addr;
    struct sockaddr_in client_addr;
    unsigned char recv_buf[1000];
    void (*init)(struct UDPServer *);
    void (*bind)(struct UDPServer *);
    void (*receive)(struct UDPServer *);
    void (*close)(struct UDPServer *);
} UDPServer;

void init_socket(UDPServer *p) {
    p->socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (-1 == p->socket_fd) {
        perror("socket");
        exit(EXIT_FAILURE);
    }
}

void bind_socket(UDPServer *p) {
    p->server_addr.sin_family = AF_INET;
    p->server_addr.sin_port = htons(SERVER_PORT);
    p->server_addr.sin_addr.s_addr = INADDR_ANY;
    memset(p->server_addr.sin_zero, 0, 8);
    if (-1 == bind(p->socket_fd, (const struct sockaddr *)&p->server_addr, sizeof(struct sockaddr))) {
        perror("bind");
        exit(EXIT_FAILURE);
    }
}

void receive_data(UDPServer *p) {
    socklen_t iAddrLen = sizeof(struct sockaddr);
    while (1) {
        int iRecvLen = recvfrom(p->socket_fd, p->recv_buf, sizeof(p->recv_buf) - 1, 0, (struct sockaddr *)&p->client_addr, &iAddrLen);
        if (iRecvLen > 0) {
            p->recv_buf[iRecvLen] = '\0';
            printf("Get Msg From %s : %s\n", inet_ntoa(p->client_addr.sin_addr), p->recv_buf);
        }
    }
}

void close_socket(UDPServer *p) {
    close(p->socket_fd);
}

int main(int argc, char **argv) {
    UDPServer server = {
        .init = init_socket,
        .bind = bind_socket,
        .receive = receive_data,
        .close = close_socket
    };

    server.init(&server);
    server.bind(&server);
    server.receive(&server);
    server.close(&server);
    return 0;
}
```

执行以下命令编译、运行：

[![8.4 UDP编程](/img/manual/image81.png)](/img/manual/image81.png)
