# 项目总结

## 一、 socket编程的步骤

+ socket是通信终端的一种抽象。进一步，TCP socket对是一个四元组，标识TCP连接的两个终端：本地IP地址、本地端口、远程IP地址、远程端口。

服务器创建一个socket并开始接受客户端连接的标准流程通常是：

1. 服务器创建一个TCP/IP socket；
2. 服务器设置一些socket选项 （常用的socket选项可见 http://blog.chinaunix.net/uid-24517549-id-4044883.html）；
3. 服务器绑定指定地址，使用bind函数分配一个地址给socket。在TCP中，调用bind可以指定一个端口号，或一个IP地址，或两者都指定，或两者都不指定；
4. 服务器让这个socket成为监听socket；
5. 服务器开始接受客户端连接。当有连接到达时，accept方法返回已连接的客户端socket；
6. 服务器从得到的客户端socket读取请求数据，回发一个响应给客户端；
7. 服务器关闭客户端连接，准备好再次接受新的客户端连接。


客户端连接服务器的过程：

1. 客户端创建一个 TCP/IP socket；
2. 客户端socket调用connect方法，使用host和port连接服务器socket；
3. 客户端socket发送请求数据；
4. 客户端socket接受服务器的响应数据。



## 二、 WSGI

### 2.1 简介

WSGI是  Python Web Server Gateway Interface 的缩写，是Python应用程序或框架与Web服务器之间的一种接口标准。

下面将对WSGI进行简要叙述，详细定义请阅读PEP0333，PEP3333是PEP0333支持Python3.x的后续版本。

[PEP0333英文版](https://www.python.org/dev/peps/pep-0333/)

[PEP0333中文版](https://github.com/mainframer/PEP333-zh-CN)

### 2.2 WSGI接口简述

+ 应用程序对象（这里用 `application` 表示）应该是一个可调用对象（callable object），即一个可以使用`()`进行调用的对象，例如方法和类；
+ 应用程序对象必须接受两个参数，这里用 `environ` 和 `start_respose` 来表示这两个参数；服务器或网关会按照 `application(environ, start_response)` 的形式调用应用程序对象，返回值是可迭代的对象；
+ `environ` 参数是一个dict，必须包含一些特定的WSGI所需的变量，具体有哪些变量请阅读PEP0333；
+ `start_response` 也是一个可调用对象，需要接受两个必需的参数（`status`， `response_headers`）和一个可选的参数 `exc_info`，返回一个可调用对象 `write(body_data)` ；
+ `status` 是一个形如 `404 Not Found` 的状态字符串； `response_headers` 是一个形如 `(header_name, header_value)` 的 tuple，用来描述HTTP的响应头；
+ `write(body_data)` 参数是一个将会被当做HTTP响应体的一部分而输出的字符串；

+ 通常来说，应用程序对象定义 `def application(environ, start_response)` ，Web服务器定义 `environ`，`start_response` ，前者用于描述服务器信息，后者用于描述响应的头部信息；
+ Web服务器在监听到一个HTTP请求后，使用 `application` 方法得到响应体，建立响应后发送给客户端。

## 三、Unix中的僵尸进程（zombie process）

以下内容部分参考了[《UNIX环境高级编程》](http://book.douban.com/subject/1788421/)第8.5节和第8.6节的内容。

进程有三种正常终止法和两种异常终止法：

+ 正常终止
    - 在main函数内执行return语句，等效于调用exit；
    - 调用exit函数。此函数由ANSI C定义，其操作包括调用各终止处理程序，然后关闭所有标准I/O流等。Unix在该定义上还有对文件描述符、多进程以及作业控制的相关定义；
    - 调用_exit系统调用函数。此函数由exit调用，它处理Unix特定的细节。_exit是由POSIX.1说明的；
+ 异常终止
    - 调用abort，它产生SIGABRT信号，是下一种异常终止的特例；
    - 当进程接收到某个信号时。进程本身（例如调用abort函数）、其他进程和内核都能产生传送到某一进程的信号。例如，进程访问越界或除0时，内核就会为该进程产生相应的信号。

对上述任一一种终止情形，我们都希望终止进程能够通知其父进程它是如何终止的，因此Unix内核会为每个终止子进程保存一定量的信息，至少包括进程ID，进程的终止状态，以及该进程使用的CPU时间总量。对于exit和_exit，这是依靠传递给它们的退出状态（exit status）参数来实现的。对于异常终止情况，终止进程的父进程通过wait或waitpid函数取得其终止状态信息。

当一个进程正常或异常终止时，内核会像其父进程发送SIGCHLD信号。因为子进程终止是个一部时间，所以这种信号是异步通知。

如果子进程在父进程之前终止，父进程可以调用wait或waitpid函数获取终止子进程的终止信息，并释放这些终止信息所占用的资源。

如果父进程在子进程之前终止，子进程的父进程会变为init进程，而只要有一个子进程终止，init进程就会调用wait函数获取其终止状态。

如果一个子进程在父进程之前终止，但父进程尚未对其进行善后处理（调用wait或waitpid获取终止信息，释放占用的资源），那么这个进程被称为僵尸进程（zombie process）。

如果僵尸进程越来越多，会占用大量系统资源，极端情况下服务器会最终耗尽资源。因此父进程一定要记得调用wait系统获取终止信息。但是，如果调用wait时没有终止的子进程，wait会将父进程阻塞掉，因此组合使用信号处理器和wait是一种更好地方法。这种组合方法的基本思路是，当一个子进程终止时，内核会发送SIGCHLD信号给父进程，父进程可以设置一个信号处理器来异步的被通知，当收到信号时，使用wait获取子进程的终止状态，从而阻止僵尸进程的出现。


需要注意的是，Windows对进程的设计中，进程相对平等，子进程可以独立的终止，不需要父进程进行回收操作，因此在Windows操作系统中不存在僵尸进程的问题。
