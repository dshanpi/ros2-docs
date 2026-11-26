---
title: "9.2 线程的控制"
sidebar_label: "9.2 线程的控制"
slug: /chapter-09/section-02/
---

## 9.2.1 多线程编临界资源访问

当线程在运行过程中，去操作公共资源，如全局变量的时候，可能会发生彼此“矛盾”现象。例如线程1企图想让变量自增，而线程2企图想要变量自减，两个线程存在互相竞争的关系导致变量永远处于一个“平衡状态”，两个线程互相竞争，线程1得到执行权后将变量自加，当线程2得到执行权后将变量自减，变量似乎永远在某个范围内浮动，无法到达期望数值，如例程9所示。

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text9.c

测试例程9：（pthread\_text9.c）

```c
1 	#define _GNU_SOURCE 
2 	#include <pthread.h>
3 	#include <stdio.h>
4 	#include <unistd.h>
5 	#include <errno.h>
6 
7 
8 	int Num = 0;
9 
10	void *fun1(void *arg)
11	{
12		while(Num < 3){
13			Num++;
14			printf("%s:Num = %d\n",__FUNCTION__,Num);
15			sleep(1);
16		}
17		pthread_exit(NULL);
18	}
19
20	void *fun2(void *arg)
21	{
22		while(Num > -3){
23			Num--;
24			printf("%s:Num = %d\n",__FUNCTION__,Num);
25			sleep(1);
26		}
27		pthread_exit(NULL);
28	}
29
30	int main()
31	{
32		int ret;
33		pthread_t tid1,tid2;
34		ret = pthread_create(&tid1,NULL,fun1,NULL);
35		if(ret != 0){
36			perror("pthread_create");
37			return -1;
38		}
39		ret = pthread_create(&tid2,NULL,fun2,NULL);
40		if(ret != 0){
41			perror("pthread_create");
42			return -1;
43		}
44		pthread_join(tid1,NULL);
45		pthread_join(tid2,NULL);
46		return 0;
47	}
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread                   
fun1:Num = 1
fun2:Num = 0
fun2:Num = 0
fun1:Num = 1
fun2:Num = -1
fun1:Num = 0
fun2:Num = -1
fun1:Num = 0
fun2:Num = -1
fun1:Num = 0
fun2:Num = -1
fun1:Num = 0
^C
```

为了解决上述对临界资源的竞争问题，pthread线程引出了互斥锁来解决临界资源访问。通过对临界资源加锁来保护资源只被单个线程操作，待操作结束后解锁，其余线程才可获得操作权。

## 9.2.2 互斥锁API简述

多个线程都要访问某个临界资源，比如某个全局变量时，需要互斥地访问：我访问时，你不能访问。

可以使用以下函数进行互斥操作。

### 1 初始化互斥量

函数原型如下：

```text
int pthread_mutex_init(phtread_mutex_t *mutex, 
const pthread_mutexattr_t *restrict attr);
```

该函数初始化一个互斥量，第一个参数是改互斥量指针，第二个参数为控制互斥量的属性，一般为NULL。当函数成功后会返回0，代表初始化互斥量成功。

当然初始化互斥量也可以调用宏来快速初始化，代码如下：

```text
pthread_mutex_t mutex = PTHREAD_MUTEX_INITALIZER; 
```

### 2 互斥量加锁/解锁

函数原型如下：

```c
互斥量加锁（阻塞）/解锁 
#include <pthread.h>
int pthread_mutex_lock(pthread_mutex_t *mutex);
int pthread_mutex_unlock(pthread_mutex_t *mutex);
成功：返回0
```

lock函数与unlock函数分别为加锁解锁函数，只需要传入已经初始化好的pthread\_mutex\_t互斥量指针。成功后会返回0。

当某一个线程获得了执行权后，执行lock函数，一旦加锁成功后，其余线程遇到lock函数时候会发生阻塞，直至获取资源的线程执行unlock函数后。unlock函数会唤醒其他正在等待互斥量的线程。

特别注意的是，当获取lock之后，必须在逻辑处理结束后执行unlock，否则会发生死锁现象！导致其余线程一直处于阻塞状态，无法执行下去。在使用互斥量的时候，尤其要注意使用pthread\_cancel函数，防止发生死锁现象！

### 3 互斥量加锁(非阻塞方式)

函数原型如下：

```c
互斥量加锁（非阻塞）
#include <pthread.h>
int pthread_mutex_trylock(pthread_mutex_t *mutex);
```

该函数同样也是一个线程加锁函数，但该函数是非阻塞模式通过返回值来判断是否加锁成功，用法与上述阻塞加锁函数一致。

### 4 互斥量加锁(非祖师方式)

函数原型如下：

```c
互斥量销毁
#include <pthread.h>
 int pthread_mutex_destory(pthread_mutex_t *mutex);
成功：返回0
```

该函数是用于销毁互斥量的，传入互斥量的指针，就可以完成互斥量的销毁，成功返回0。

### 5 程序示例

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text10.c

测试例程10：（pthread\_text10.c）

```c
1 	#define _GNU_SOURCE 
2 	#include <pthread.h>
3 	#include <stdio.h>
4 	#include <unistd.h>
5 	#include <errno.h>
6 
7 	pthread_mutex_t mutex;//互斥量变量 一般申请全局变量
8 
9 	int Num = 0;//公共临界变量
10
11	void *fun1(void *arg)
12	{
13		pthread_mutex_lock(&mutex);//加锁 若有线程获得锁，则会阻塞
14		while(Num < 3){
15			Num++;
16			printf("%s:Num = %d\n",__FUNCTION__,Num);
17			sleep(1);
18		}
19		pthread_mutex_unlock(&mutex);//解锁
20		pthread_exit(NULL);//线程退出 pthread_join会回收资源
21	}
22
23	void *fun2(void *arg)
24	{
25		pthread_mutex_lock(&mutex);//加锁 若有线程获得锁，则会阻塞
26		while(Num > -3){
27			Num--;
28			printf("%s:Num = %d\n",__FUNCTION__,Num);
29			sleep(1);
30		}
31		pthread_mutex_unlock(&mutex);//解锁
32		pthread_exit(NULL);//线程退出 pthread_join会回收资源
33	}
34
35	int main()
36	{
37		int ret;
38		pthread_t tid1,tid2;
39		ret = pthread_mutex_init(&mutex,NULL);//初始化互斥量
40		if(ret != 0){
41			perror("pthread_mutex_init");
42			return -1;
43		}
44		ret = pthread_create(&tid1,NULL,fun1,NULL);//创建线程1
45		if(ret != 0){
46			perror("pthread_create");
47			return -1;
48		}
49		ret = pthread_create(&tid2,NULL,fun2,NULL);//创建线程2
50		if(ret != 0){
51			perror("pthread_create");
52			return -1;
53		}
54		pthread_join(tid1,NULL);//阻塞回收线程1
55		pthread_join(tid2,NULL);//阻塞回收线程2
56		pthread_mutex_destroy(&mutex);//销毁互斥量
57		return 0;
58	}
59
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text10.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread
fun1:Num = 1
fun1:Num = 2
fun1:Num = 3
fun2:Num = 2
fun2:Num = 1
fun2:Num = 0
fun2:Num = -1
fun2:Num = -2
fun2:Num = -3
```

上述例程通过加入互斥量，保证了临界变量某一时刻只被某一线程控制，实现了临界资源的控制。需要说明的是，线程加锁在循环内与循环外的情况。本历程在进入while循环前进行了加锁操作，在循环结束后进行的解锁操作，如果将加锁解锁全部放入while循环内，作为单核的机器，执行结果无异，当有多核机器执行代码时，可能会发生“抢锁”现象，这取决于操作系统底层的实现。

## 9.2.3 多线程编执行顺序控制

解决了临界资源的访问，但似乎对线程的执行顺序无法得到控制，因线程都是无序执行，之前采用sleep强行延时的方法勉强可以控制执行顺序，但此方法在实际项目情况往往是不可取的，其仅仅可解决线程创建的顺序，当创建之后执行的顺序又不会受到控制，于是便引入了信号量的概念，解决线程执行顺序。

例程11将展示线程的执行的随机性。

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text11.c

测试例程11：（pthread\_text11.c）

```c
1 	#define _GNU_SOURCE 
2 	#include <pthread.h>
3 	#include <stdio.h>
4 	#include <unistd.h>
5 	#include <errno.h>
6 
7 	void *fun1(void *arg)
8 	{
9 		printf("%s:Pthread Come!\n",__FUNCTION__);
10		pthread_exit(NULL);
11	}
12
13	void *fun2(void *arg)
14	{
15		printf("%s:Pthread Come!\n",__FUNCTION__);
16		pthread_exit(NULL);
17	}
18
19	void *fun3(void *arg)
20	{
21		printf("%s:Pthread Come!\n",__FUNCTION__);
22		pthread_exit(NULL);
23	}
24
25	int main()
26	{
27		int ret;
28		pthread_t tid1,tid2,tid3;
29		ret = pthread_create(&tid1,NULL,fun1,NULL);
30		if(ret != 0){
31			perror("pthread_create");
32			return -1;
33		}
34		ret = pthread_create(&tid2,NULL,fun2,NULL);
35		if(ret != 0){
36			perror("pthread_create");
37			return -1;
38		}
39		ret = pthread_create(&tid3,NULL,fun3,NULL);
40		if(ret != 0){
41			perror("pthread_create");
42			return -1;
43		}
44		pthread_join(tid1,NULL);
45		pthread_join(tid2,NULL);
46		pthread_join(tid3,NULL);
47		return 0;
48	}
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text11.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread
fun1:Pthread Come!
fun2:Pthread Come!
fun3:Pthread Come!
```

通过上述例程可以发现，多次执行该函数其次序是无序的，线程之间的竞争无法控制，通过使用信号量来使得线程顺序为可控的。

## 9.2.4 信号量API简述

注意：信号量跟互斥量不一样，互斥量用来防止多个线程同时访问某个临界资源。信号量起通知作用，线程A在等待某件事，线程B完成了这件事后就可以给线程A发信号。

### 1 初始化信号量

函数原型如下：

```text
int sem_init(sem_t *sem,int pshared,unsigned int value);
```

- 该函数可以初始化一个信号量，第一个参数传入sem\_t类型指针；

- 第二个参数传入0代表线程控制，否则为进程控制；

- 第三个参数表示信号量的初始值，0代表阻塞，1代表运行。

- 待初始化结束信号量后，若执行成功会返回0。

### 2 2. 信号量P/V操作

函数原型如下：

```c
#include <pthread.h>
int sem_wait(sem_t *sem);
int sem_post(sem_t *sem);
成功：返回0
```

- sem\_wait函数作用为检测指定信号量是否有资源可用，若无资源可用会阻塞等待，若有资源可用会自动的执行“sem-1”的操作。所谓的“sem-1”是与上述初始化函数中第三个参数值一致，成功执行会返回0。

- sem\_post函数会释放指定信号量的资源，执行“sem+1”操作。

通过以上2个函数可以完成所谓的PV操作，即信号量的申请与释放，完成对线程执行顺序的控制。

### 3 信号量申请(非阻塞方式)

函数原型如下：

```c
#include <pthread.h>
int sem_trywait(sem_t *sem);
成功：返回0
```

此函数是信号量申请资源的非阻塞函数，功能与sem\_wait一致，唯一区别在于此函数为非阻塞。

### 4 信号量销毁

函数原型如下：

```c
#include <pthread.h>
int sem_destory(sem_t *sem);
成功：返回0
```

该函数为信号量销毁函数，执行过后可将信号量进行销毁。

### 5 程序示例

本节源码位于如下目录：

sources\\09\_thread\\pthread\_text12.c

测试例程12：（pthread\_text12.c）

```c
1 	#define _GNU_SOURCE 
2 	#include <pthread.h>
3 	#include <stdio.h>
4 	#include <unistd.h>
5 	#include <errno.h>
6 	#include <semaphore.h>
7 
8 	sem_t sem1,sem2,sem3;//申请的三个信号量变量
9 
10	void *fun1(void *arg)
11	{
12		sem_wait(&sem1);//因sem1本身有资源，所以不被阻塞 获取后sem1-1 下次会会阻塞
13		printf("%s:Pthread Come!\n",__FUNCTION__);
14		sem_post(&sem2);// 使得sem2获取到资源
15		pthread_exit(NULL);
16	}
17
18	void *fun2(void *arg)
19	{
20		sem_wait(&sem2);//因sem2在初始化时无资源会被阻塞，直至14行代码执行 不被阻塞 sem2-1 下次会阻塞
21		printf("%s:Pthread Come!\n",__FUNCTION__);
22		sem_post(&sem3);// 使得sem3获取到资源
23		pthread_exit(NULL);
24	}
25
26	void *fun3(void *arg)
27	{
28		sem_wait(&sem3);//因sem3在初始化时无资源会被阻塞，直至22行代码执行 不被阻塞 sem3-1 下次会阻塞
29		printf("%s:Pthread Come!\n",__FUNCTION__);
30		sem_post(&sem1);// 使得sem1获取到资源
31		pthread_exit(NULL);
32	}
33
34	int main()
35	{
36		int ret;
37		pthread_t tid1,tid2,tid3;
38		ret = sem_init(&sem1,0,1);  //初始化信号量1 并且赋予其资源
39		if(ret < 0){
40			perror("sem_init");
41			return -1;
42		}
43		ret = sem_init(&sem2,0,0); //初始化信号量2 让其阻塞
44		if(ret < 0){
45			perror("sem_init");
46			return -1;
47		}
48		ret = sem_init(&sem3,0,0); //初始化信号3 让其阻塞
49		if(ret < 0){
50			perror("sem_init");
51			return -1;
52		}
53		ret = pthread_create(&tid1,NULL,fun1,NULL);//创建线程1
54		if(ret != 0){
55			perror("pthread_create");
56			return -1;
57		}
58		ret = pthread_create(&tid2,NULL,fun2,NULL);//创建线程2
59		if(ret != 0){
60			perror("pthread_create");
61			return -1;
62		}
63		ret = pthread_create(&tid3,NULL,fun3,NULL);//创建线程3
64		if(ret != 0){
65			perror("pthread_create");
66			return -1;
67		}
68		/*回收线程资源*/
69		pthread_join(tid1,NULL);
70		pthread_join(tid2,NULL);
71		pthread_join(tid3,NULL);
72
73		/*销毁信号量*/
74		sem_destroy(&sem1);
75		sem_destroy(&sem2);
76		sem_destroy(&sem3);
78		return 0;
79	}
```

运行结果：

```bash
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ gcc pthread_text12.c -o pthread -lpthread
user@spacemit-k1-x-MUSE-Pi-Pro-board:~/C_Test/09_pthread$ ./pthread
fun1:Pthread Come!
fun2:Pthread Come!
fun3:Pthread Come
```

该例程加入了信号量，使得线程的执行顺序变为可控的。在初始化信号量时，将信号量1填入资源，第一个线程调用sem\_wait函数可以成功获得信号量，在执行完逻辑后使用sem\_pos函数来释放。当执行函数sem\_wait后，会执行sem自减操作，使下一次竞争被阻塞，直至通过sem\_pos被释放。

上述例程因38行初始化信号量1时候，使其默认获取到资源；第43、48行初始化信号量2、3时候，使之没有资源。于是在线程处理函数中，每个线程通过sem\_wait函数来等待资源，发生阻塞。因信号量1初始值为有资源，故可以先执行线程1的逻辑。待执行完第12行sem\_wait函数，会导致sem1-1，使得下一次此线程会被阻塞。继而执行至14行，通过sem\_post函数使sem2信号量获取资源，从而冲破阻塞执行线程2的逻辑...以此类推完成线程的有序控制。

## 9.2.5 条件变量

参考《Unix\_Linux\_Windows\_OpenMP多线程编程.pdf》，作者不详。

条件变量时一种同步机制，用来通知其他线程条件满足了。一般是用来通知对方共享数据的状态信息，因此条件变量时结合互斥量来使用的。

### 1 创建和销毁条件变量

函数原型如下：

```c
#include <pthread.h>
// 初始化条件变量
pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
int pthread_cond_init(pthread_cond_t *cond, pthread_condattr_t *cond_attr);//cond_attr通常为NULL
// 销毁条件变量
int pthread_cond_destroy(pthread_cond_t *cond);
这些函数成功时都返回0
```

### 2 等待条件变量

函数原型如下：

```text
int pthread_cond_wait(pthread_cond_t *cond, pthread_mutex_t *mutex);
```

这需要结合互斥量一起使用，示例代码如下：

```text
pthread_mutex_lock(&g_tMutex);
// 如果条件不满足则，会unlock g_tMutex  
// 条件满足后被唤醒，会lock g_tMutex
pthread_cond_wait(&g_tConVar, &g_tMutex); 
/* 操作临界资源 */
pthread_mutex_unlock(&g_tMutex);
```

### 3 通知条件变量

函数原型如下：

```text
int pthread_cond_signal(pthread_cond_t *cond);
```

pthread\_cond\_signal函数只会唤醒一个等待cond条件变量的线程，示例代码如下：

```text
pthread_cond_signal(&g_tConVar);
```
