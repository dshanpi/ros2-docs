---
title: "8.3 TCP编程"
sidebar_label: "8.3 TCP编程"
slug: /chapter-08/section-03/
---

本节源码位于如下目录：

sources\\08\_socket\\01\_tcp\\

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

typedef struct SocketClient {
    int fd;
    struct sockaddr_in server_addr;
    char send_buf[1000];
    
    int (*init)(struct SocketClient *p);
    int (*connect)(struct SocketClient *p, const char *ip);
    int (*send_data)(struct SocketClient *p);
    void (*close)(struct SocketClient *p);
} SocketClient;

int init_socket(struct SocketClient *p) {
    p->fd = socket(AF_INET, SOCK_STREAM, 0);
    return p->fd == -1 ? -1 : 0;
}

int connect_server(struct SocketClient *p, const char *ip) {
    p->server_addr.sin_family = AF_INET;
    p->server_addr.sin_port = htons(SERVER_PORT);
    if (0 == inet_aton(ip, &p->server_addr.sin_addr)) {
        return -1;
    }
    memset(p->server_addr.sin_zero, 0, 8);
    return connect(p->fd, (const struct sockaddr *)&p->server_addr, sizeof(struct sockaddr));
}

int send_to_server(struct SocketClient *p) {
    int send_len = send(p->fd, p->send_buf, strlen(p->send_buf), 0);
    return send_len <= 0 ? -1 : 0;
}

void close_socket(struct SocketClient *p) {
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

	SocketClient client = {
		.init = init_socket,
		.connect = connect_server,
		.send_data = send_to_server,
		.close = close_socket
	};

	if ((*(client.init))(&client) == -1) {
		printf("socket init failed\n");
		return -1;
	}

	if ((*(client.connect))(&client, argv[1]) == -1) {
		printf("connect error!\n");
		(*(client.close))(&client);
		return -1;
	}

	printf("Connected to server. Type messages to send:\n");
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
#define BACKLOG     10

struct SocketServer {
    int socket_fd;
    struct sockaddr_in server_addr;
    struct sockaddr_in client_addr;
    int client_count;
    int (*init)(struct SocketServer *p);
    int (*bind)(struct SocketServer *p);
    int (*listen)(struct SocketServer *p);
    int (*accept)(struct SocketServer *p);
    void (*handle_client)(struct SocketServer *p);
};

int init_socket(struct SocketServer *p) {
    p->socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (p->socket_fd == -1) {
        perror("socket");
        return -1;
    }
    return 0;
}

int bind_socket(struct SocketServer *p) {
    p->server_addr.sin_family = AF_INET;
    p->server_addr.sin_port = htons(SERVER_PORT);
    p->server_addr.sin_addr.s_addr = INADDR_ANY;
    memset(p->server_addr.sin_zero, 0, 8);
    int ret = bind(p->socket_fd, (const struct sockaddr *)&p->server_addr, sizeof(struct sockaddr));
    if (ret == -1) {
        perror("bind");
        return -1;
    }
    return 0;
}

int listen_socket(struct SocketServer *p) {
    int ret = listen(p->socket_fd, BACKLOG);
    if (ret == -1) {
        perror("listen");
        return -1;
    }
    return 0;
}

int accept_client(struct SocketServer *p) {
    socklen_t addr_len = sizeof(struct sockaddr);
    p->client_count++;
    int client_fd = accept(p->socket_fd, (struct sockaddr *)&p->client_addr, &addr_len);
    if (client_fd == -1) {
        perror("accept");
        return -1;
    }
    printf("Get connect from client %d : %s\n", p->client_count, inet_ntoa(p->client_addr.sin_addr));
    return client_fd;
}

void handle_client(struct SocketServer *p) {
    int client_fd = p->accept(p);
    if (client_fd != -1) {
        if (!fork()) {
            unsigned char recv_buf[1000];
            int recv_len;
            while (1) {
                recv_len = recv(client_fd, recv_buf, 999, 0);
                if (recv_len <= 0) {
                    close(client_fd);
                    exit(0);
                } else {
                    recv_buf[recv_len] = '\0';
                    printf("Get Msg From Client %d: %s\n", p->client_count, recv_buf);
                }
            }
        }
    }
}

int main(int argc, char **argv) {
    signal(SIGCHLD, SIG_IGN);
    struct SocketServer server = {
        .init = init_socket,
        .bind = bind_socket,
        .listen = listen_socket,
        .accept = accept_client,
        .handle_client = handle_client
    };
    if (server.init(&server) == -1 || server.bind(&server) == -1 || server.listen(&server) == -1) {
        return -1;
    }
    while (1) {
        server.handle_client(&server);
    }
    close(server.socket_fd);
    return 0;
}
```

执行以下指令编译、运行：

[![8.3 TCP编程](/img/manual/image80.png)](/img/manual/image80.png)
