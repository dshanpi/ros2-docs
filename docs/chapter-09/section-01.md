---
title: "9.1 线程的使用"
sidebar_label: "9.1 线程的使用"
slug: /chapter-09/section-01/
---

## 9.1.1 为什么要使用多线程

在编写代码时，是否会遇到以下的场景会感觉到难以下手？

要做2件事，一件需要阻塞等待，另一件需要实时进行。例如播放器：一边在屏幕上播放视频，一边在等待用户的按键操作。如果使用单线程的话，程序必须一会查询有无按键，一会播放视频。查询按键太久，就会导致视频播放卡顿；视频播放太久，就无法及时响应用户的操作。并且查询按键和播放视频的代码混杂在一起，代码丑陋。

如果使用多线程，线程1单独处理按键，线程2单独处理播放，可以完美解决上述问题。

## 9.1.2 线程概念

所谓线程，就是操作系统所能调度的最小单位。普通的进程，只有一个线程在执行对应的逻辑。我们可以通过多线程编程，使一个进程可以去执行多个不同的任务。相比多进程编程而言，线程享有共享资源，即在进程中出现的全局变量，每个线程都可以去访问它，与进程共享“4G”内存空间，使得系统资源消耗减少。本章节来讨论Linux下POSIX线程。

## 9.1.3 线程的标识pthread\_t

对于进程而言，每一个进程都有一个唯一对应的PID号来表示该进程，而对于线程而言，也有一个“类似于进程的PID号”，名为tid，其本质是一个pthread\_t类型的变量。线程号与进程号是表示线程和进程的唯一标识，但是对于线程号而言，其仅仅在其所属的进程上下文中才有意义。

```c
获取线程号
#include <pthread.h>
pthread_t pthread_self(void);
成功：返回线程号
```

在程序中，可以通过函数pthread\_self，来返回当前线程的线程号，例程1给出了打印线程tid号。

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text1.c

测试例程1：（pthread\_text1.c）

```c
1	#include <pthread.h>
2	#include <stdio.h>
3
4	int main()
5	{
6		pthread_t tid = pthread_self();//获取主线程的tid号
7		printf("tid = %lu\n",(unsigned long)tid);
8       return 0;
9	}
```

<strong>注意：</strong>因采用POSIX线程接口，故在要编译的时候包含pthread库，使用gcc编译应gcc xxx.c -lpthread 方可编译多线程程序。

编译结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text1.c -o pthread_text1 -lpthread 
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ls
pthread_text1  phtread_txex1.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread_text1 
tid = 273004842080
```

## 9.1.4 线程的创建

怎么创建线程呢？使用pthread\_create函数：

```c
创建线程
#include <pthread.h>
int pthread_create(pthread_t *thread, const pthread_attr_t *attr,void *(*start_routine) (void *), void *arg);
```

- 该函数第一个参数为pthread\_t指针，用来保存新建线程的线程号；

- 第二个参数表示了线程的属性，一般传入NULL表示默认属性；

- 第三个参数是一个函数指针，就是线程执行的函数。这个函数返回值为void\*，形参为void\*。

- 第四个参数则表示为向线程处理函数传入的参数，若不传入，可用NULL填充，有关线程传参后续小节会有详细的说明，

接下来通过一个简单例程来使用该函数创建出一个线程。本节源码位于如下目录：

sources\\09\_thread\\pthread\_text2.c

测试例程2：（pthread\_text2.c）

```c
1 	#include <pthread.h>
2 	#include <stdio.h>
3 	#include <unistd.h>
4 	#include <errno.h>
5 
6 	void *fun(void *arg)
7 	{
8 		printf("pthread_New = %lu\n",(unsigned long)pthread_self());//打印线程的tid号
9 	}
10
11	int main()
12	{
13
14		pthread_t tid1;
15		int ret = pthread_create(&tid1,NULL,fun,NULL);//创建线程
16		if(ret != 0){
17			perror("pthread_create");
18			return -1;
19		}
20
21		/*tid_main 为通过pthread_self获取的线程ID，tid_new通过执行pthread_create成功后tid指向的空间*/
22		printf("tid_main = %lu tid_new = %lu \n",(unsigned long)pthread_self(),(unsigned long)tid1);
23		
24		/*因线程执行顺序随机，不加sleep可能导致主线程先执行，导致进程结束，无法执行到子线程*/
25		sleep(1);
26
27		return 0;
28	}
```

```text
29
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text2.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread 
tid_main = 273131994240 tid_new = 273130422656 
pthread_New = 273130422656
```

通过pthread\_create确实可以创建出来线程，主线程中执行pthread\_create后的tid指向了线程号空间，与子线程通过函数pthread\_self打印出来的线程号一致。

特别说明的是，当主线程伴随进程结束时，所创建出来的线程也会立即结束，不会继续执行。并且创建出来的线程的执行顺序是随机竞争的，并不能保证哪一个线程会先运行。可以将上述代码中sleep函数进行注释，观察实验现象。

去掉上述代码25行后运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread
tid_main = 273570823296 tid_new = 273569251712
```

上述运行代码3次，其中有2次被进程结束，无法执行到子线程的逻辑，最后一次则执行到了子线程逻辑后结束的进程。如此可以说明，线程的执行顺序不受控制，且整个进程结束后所产生的线程也随之被释放，在后续内容中将会描述如何控制线程执行。

## 9.1.5 向线程传入参数

pthread\_create()的最后一个参数的为void\*类型的数据，表示可以向线程传递一个void\*数据类型的参数，线程的回调函数中可以获取该参数，例程3举例了如何向线程传入变量地址与变量值。

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text3.c

测试例程3：（pthread\_text3.c）

```c
1 	#include <pthread.h>
2 	#include <stdio.h>
3 	#include <unistd.h>
4 	#include <errno.h>
5 
6 	void *fun1(void *arg)
7 	{
8 		printf("%s:arg = %d Addr = %p\n",__FUNCTION__,*(int *)arg,arg);
9 	}
10
11	void *fun2(void *arg)
12	{
13		printf("%s:arg = %d Addr = %p\n",__FUNCTION__,(int)(long)arg,arg);
14	}
15
16	int main()
17	{
18
19		pthread_t tid1,tid2;
20		int a = 50;
21		int ret = pthread_create(&tid1,NULL,fun1,(void *)&a);//创建线程传入变量a的地址
22		if(ret != 0){
23			perror("pthread_create");
24			return -1;
25		}
27		ret = pthread_create(&tid2,NULL,fun2,(void *)(long)a);//创建线程传入变量a的值
28		if(ret != 0){
29			perror("pthread_create");
30			return -1;
31		}
32		sleep(1);
33		printf("%s:a = %d Add = %p \n",__FUNCTION__,a,&a);
34		return 0;
35	}
36
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text3.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ls
pthread_text1  pthread_text1.c  pthread  pthread_text2.c  pthread_text3.c
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread 
fun1:arg = 50 Addr = 0x3fc8c2cc10
fun2:arg = 50 Addr = 0x32
main:a = 50 Add = 0x3fc8c2cc10
```

本例程展示了如何利用线程创建函数的第四个参数向线程传入数据，举例了如何以地址的方式传入值、以变量的方式传入值，例程代码的21行，是将变量a先行取地址后，再次强制类型转化为void\*后传入线程，线程处理的回调函数中，先将万能指针void\*转化为int\*，再次取地址就可以获得该地址变量的值，其本质在于地址的传递。例程代码的27行，直接将int类型的变量强制转化为void\*进行传递（针对不同位数机器，指针对其字数不同，需要int转化为long在转指针，否则可能会发生警告），在线程处理回调函数中，直接将void\*数据转化为int类型即可，本质上是在传递变量a的值。

上述两种方法均可得到所要的值，但是要注意其本质，一个为地址传递，一个为值的传递。当变量发生改变时候，传递地址后，该地址所对应的变量也会发生改变，但传入变量值的时候，即使地址指针所指的变量发生变化，但传入的为变量值，不会受到指针的指向的影响，实际项目中切记两者之间的区别。具体说明见例程4。

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text4.c

测试例程4：（pthread\_text4.c）

```c
1 	#include <pthread.h>
2 	#include <stdio.h>
3 	#include <unistd.h>
4 	#include <errno.h>
5 
6 	void *fun1(void *arg)
7 	{
8 		while(1){
9 		
10			printf("%s:arg = %d Addr = %p\n",__FUNCTION__,*(int *)arg,arg);
11			sleep(1);
12		}
13	}
14
15	void *fun2(void *arg)
16	{
17		while(1){
18		
19			printf("%s:arg = %d Addr = %p\n",__FUNCTION__,(int)(long)arg,arg);
20			sleep(1);
21		}
22	}
23
24	int main()
25	{
26
27		pthread_t tid1,tid2;
28		int a = 50;
29		int ret = pthread_create(&tid1,NULL,fun1,(void *)&a);
30		if(ret != 0){
31			perror("pthread_create");
32			return -1;
33		}
34		sleep(1);
35		ret = pthread_create(&tid2,NULL,fun2,(void *)(long)a);
36		if(ret != 0){
37			perror("pthread_create");
38			return -1;
39		}
40		while(1){
41			a++;
42			sleep(1);
43			printf("%s:a = %d Add = %p \n",__FUNCTION__,a,&a);
44		}
45		return 0;
46	}
```

```text
47
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text4.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread 
fun1:arg = 50 Addr = 0x3fe02dfc10
fun1:arg = 50 Addr = 0x3fe02dfc10
fun2:arg = 50 Addr = 0x32
main:a = 51 Add = 0x3fe02dfc10 
fun2:arg = 50 Addr = 0x32
fun1:arg = 51 Addr = 0x3fe02dfc10
main:a = 52 Add = 0x3fe02dfc10 
fun2:arg = 50 Addr = 0x32
fun1:arg = 53 Addr = 0x3fe02dfc10
main:a = 53 Add = 0x3fe02dfc10 
fun2:arg = 50 Addr = 0x32
fun1:arg = 54 Addr = 0x3fe02dfc10
main:a = 54 Add = 0x3fe02dfc10 
fun1:arg = 54 Addr = 0x3fe02dfc10
fun2:arg = 50 Addr = 0x32
^C
```

上述例程讲述了如何向线程传递一个参数，在处理实际项目中，往往会遇到传递多个参数的问题，我们可以通过结构体来进行传递，解决此问题。

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text5.c

测试例程5：（pthread\_text5.c）

```c
1 	#include <pthread.h>
2 	#include <stdio.h>
3 	#include <unistd.h>
4 	#include <string.h>
5 	#include <errno.h>
6 
7 	struct Stu{
8 		int Id;
9 		char Name[32];
10		float Mark;
11	};
12
13	void *fun1(void *arg)
14	{
15		struct Stu *tmp = (struct Stu *)arg;
16		printf("%s:Id = %d Name = %s Mark = %.2f\n",__FUNCTION__,tmp->Id,tmp->Name,tmp->Mark);
17		
18	}
19
20	int main()
21	{
22
23		pthread_t tid1,tid2;
24		struct Stu stu;
25		stu.Id = 10000;
26		strcpy(stu.Name,"ZhangSan");
27		stu.Mark = 94.6;
28
29		int ret = pthread_create(&tid1,NULL,fun1,(void *)&stu);
30		if(ret != 0){
31			perror("pthread_create");
32			return -1;
33		}
34		printf("%s:Id = %d Name = %s Mark = %.2f\n",__FUNCTION__,stu.Id,stu.Name,stu.Mark);
35		sleep(1);
36		return 0;
37	}
```

```text
38
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread                   
main:Id = 10000 Name = ZhangSan Mark = 94.60
fun1:Id = 10000 Name = ZhangSan Mark = 94.60
```

## 9.1.6 线程的退出与回收

线程的退出情况有三种：第一种是进程结束，进程中所有的线程也会随之结束。第二种是通过函数pthread\_exit来主动的退出线程。第三种被其他线程调用pthread\_cancel来被动退出。

当线程结束后，主线程可以通过函数pthread\_join/pthread\_tryjoin\_np来回收线程的资源，并且获得线程结束后需要返回的数据。

### 1 线程主动退出

pthread\_exit函数原型如下：

```c
线程主动退出
#include <pthread.h>
void pthread_exit(void *retval);
```

pthread\_exit函数为线程退出函数，在退出时候可以传递一个void\*类型的数据带给主线程，若选择不传出数据，可将参数填充为NULL。

### 2 线程被动退出

pthread\_cancel函数原型如下：

```c
线程被动退出，其他线程使用该函数让另一个线程退出
#include <pthread.h>
int pthread_cancel(pthread_t thread);
成功：返回0
```

该函数传入一个tid号，会强制退出该tid所指向的线程，若成功执行会返回0。

### 3 线程资源回收(阻塞方式)

pthread\_join函数原型如下：

```c
线程资源回收（阻塞）
#include <pthread.h>
int pthread_join(pthread_t thread, void **retval);
```

该函数为线程回收函数，默认状态为阻塞状态，直到成功回收线程后才返回。第一个参数为要回收线程的tid号，第二个参数为线程回收后接受线程传出的数据。

### 4 线程资源回收(非阻塞方式)

pthread\_tryjoin\_np函数原型如下：

```c
线程资源回收（非阻塞）
#define _GNU_SOURCE            
#include <pthread.h>
int pthread_tryjoin_np(pthread_t thread, void **retval);
```

该函数为非阻塞模式回收函数，通过返回值判断是否回收掉线程，成功回收则返回0，其余参数与pthread\_join一致。

### 5 程序示例1

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text6.c

测试例程6：（pthread\_text6.c）

```c
1 	#include <pthread.h>
2 	#include <stdio.h>
3 	#include <unistd.h>
4 	#include <errno.h>
5 
6 	void *fun1(void *arg)
7 	{
8 		static int tmp = 0;//必须要static修饰，否则pthread_join无法获取到正确值
9 		//int tmp = 0;
10		tmp = *(int *)arg;
11		tmp+=100;
12		printf("%s:Addr = %p tmp = %d\n",__FUNCTION__,&tmp,tmp);
13		pthread_exit((void *)&tmp);//将变量tmp取地址转化为void*类型传出
14	}
15
16
17	int main()
18	{
19
20		pthread_t tid1;
21		int a = 50;
22		void *Tmp = NULL;//因pthread_join第二个参数为void**类型
23		int ret = pthread_create(&tid1,NULL,fun1,(void *)&a);
24		if(ret != 0){
25			perror("pthread_create");
26			return -1;
27		}
28		pthread_join(tid1,&Tmp);
29		printf("%s:Addr = %p Val = %d\n",__FUNCTION__,Tmp,*(int *)Tmp);
30		return 0;
31	}
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text6.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread 
fun1:Addr = 0x12054 tmp = 150
main:Addr = 0x12054 Val = 150
```

上述例程先通过23行将变量以地址的形式传入线程，在线程中做出了自加100的操作，当线程退出的时候通过线程传参，用void\*类型的数据通过pthread\_join接受。此例程去掉了之前加入的sleep函数，原因是pthread\_join函数具备阻塞的特性，直至成功收回掉线程后才会冲破阻塞，因此不需要靠考虑主线程会执行到30行结束进程的情况。特别要说明的是例程第8行，当变量从线程传出的时候，需要加static修饰，对生命周期做出延续，否则无法传出正确的变量值。

### 6 程序示例2

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text7.c

测试例程7：（pthread\_text7.c）

```c
1 	#define _GNU_SOURCE 
2 	#include <pthread.h>
3 	#include <stdio.h>
4 	#include <unistd.h>
5 	#include <errno.h>
6 
7 	void *fun(void *arg)
8 	{
9 		printf("Pthread:%d Come !\n",(int )(long)arg+1);
10		pthread_exit(arg);
11	}
12
13
14	int main()
15	{
16		int ret,i,flag = 0;
17		void *Tmp = NULL;
18		pthread_t tid[3];
19		for(i = 0;i < 3;i++){
20			ret = pthread_create(&tid[i],NULL,fun,(void *)(long)i);
21			if(ret != 0){
22				perror("pthread_create");
23				return -1;
24			}
25		}
26		while(1){//通过非阻塞方式收回线程，每次成功回收一个线程变量自增，直至3个线程全数回收
27			for(i = 0;i <3;i++){
28				if(pthread_tryjoin_np(tid[i],&Tmp) == 0){
29					printf("Pthread : %d exit !\n",(int )(long )Tmp+1);
30					flag++;	
31				}
32			}
33			if(flag >= 3) break;
34		}
35		return 0;
36	}
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text7.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread 
Pthread:1 Come !
Pthread:2 Come !
Pthread:3 Come !
Pthread : 1 exit !
Pthread : 2 exit !
Pthread : 3 exit !
```

例程7展示了如何使用非阻塞方式来回收线程，此外也展示了多个线程可以指向同一个回调函数的情况。例程6通过阻塞方式回收线程几乎规定了线程回收的顺序，若最先回收的线程未退出，则一直会被阻塞，导致后续先退出的线程无法及时的回收。

通过函数pthread\_tryjoin\_np，使用非阻塞回收，线程可以根据退出先后顺序自由的进行资源的回收。

### 7 程序示例3

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text8.c

测试例程8：（pthread\_text8.c）

```c
1 	#define _GNU_SOURCE 
2 	#include <pthread.h>
3 	#include <stdio.h>
4 	#include <unistd.h>
5 	#include <errno.h>
6 
7 	void *fun1(void *arg)
8 	{
9 		printf("Pthread:1 come!\n");
10		while(1){
11			sleep(1);
12		}
13	}
14
15	void *fun2(void *arg)
16	{
17		printf("Pthread:2 come!\n");
18		pthread_cancel((pthread_t )(long)arg);//杀死线程1，使之强制退出
19		pthread_exit(NULL);
20	}
21
22	int main()
23	{
24		int ret,i,flag = 0;
25		void *Tmp = NULL;
26		pthread_t tid[2];
27		ret = pthread_create(&tid[0],NULL,fun1,NULL);
28		if(ret != 0){
29			perror("pthread_create");
30			return -1;
31		}
32		sleep(1);
33		ret = pthread_create(&tid[1],NULL,fun2,(void *)tid[0]);//传输线程1的线程号
34		if(ret != 0){
35			perror("pthread_create");
36			return -1;
37		}
38		while(1){//通过非阻塞方式收回线程，每次成功回收一个线程变量自增，直至2个线程全数回收

39			for(i = 0;i <2;i++){
40				if(pthread_tryjoin_np(tid[i],NULL) == 0){
41					printf("Pthread : %d exit !\n",i+1);
42					flag++;	
43				}
44			}
45			if(flag >= 2) break;
46		}
47		return 0;
48	}
49
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text8.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread
Pthread:1 come!
Pthread:2 come!
Pthread : 2 exit !
Pthread : 1 exit !
```

例程8展示了如何利用pthread\_cancel函数主动的将某个线程结束。27行与33行创建了线程，将第一个线程的线程号传参形式传入了第二个线程。第一个的线程执行死循环睡眠逻辑，理论上除非进程结束，其永远不会结束，但在第二个线程中调用了pthread\_cancel函数，相当于向该线程发送一个退出的指令，导致线程被退出，最终资源被非阻塞回收掉。此例程要注意第32行的sleep函数，一定要确保线程1先执行，因线程是无序执行，故加入该睡眠函数控制顺序，在本章后续，会讲解通过加锁、信号量等手段来合理的控制线程的临界资源访问与线程执行顺序控制。
