# 项目总结

## 一、 socket编程的步骤

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

