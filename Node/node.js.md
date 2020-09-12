<link rel="stylesheet" type="text/css" href="Style/markdown-style.css" />

# Node.js

## Introduction

Node. js is a platform built on Chrome's JavaScript runtime for easily building fast and scalable network applications. Node. js uses an event-driven, non-blocking I/O model that makes it lightweight and efficient, perfect for data-intensive real-time applications that run across distributed devices.

Here is a more simple way of what node.js is:

` Node.js = Runtime Environment + JavaScript Library `

### Features of Node.js
The following are some of the important features that make Node.js the first choice of software architects.

- **Asynchronous and Event Driven** - All APIs of Node.js library are asynchronous, that is, non-blocking. It essentially means a Node.js based server never waits for an API to return data. The server moves to the next API after calling it and a notification mechanism of Events of Node.js helps the server to get a response from the previous API call.
- **Very Fast** - Being built on Google Chrome's V8 JavaScript Engine, Node.js library is very fast in code execution.
- **Single Threaded but Highly Scalable** - Node.js uses a single threaded model with event looping. Event mechanism helps the server to respond in a non-blocking way and makes the server highly scalable as opposed to traditional servers which create limited threads to handle requests. Node.js uses a single threaded program and the same program can provide service to a much larger number of requests than traditional servers like Apache HTTP Server.
- **No Buffering** - Node.js applications never buffer any data. These applications simply output the data in chunks.
- **License** - Node.js is released under the MIT license[<img src="https://www.pngfind.com/pngs/m/88-882006_shares-svg-png-icon-shares-icon-transparent-png.png" height="10px" width="10px" />](https://raw.githubusercontent.com/joyent/node/v0.12.0/LICENSE).

### Who uses Node.js?

- [Projects, Applications, and Companies Using Node<img src="https://www.pngfind.com/pngs/m/88-882006_shares-svg-png-icon-shares-icon-transparent-png.png" height="10px" width="10px" />](https://github.com/nodejs/node-v0.x-archive/wiki/projects,-applications,-and-companies-using-node)

### Concepts
The following diagram depicts some important parts of Node.js which we will discuss in detail in the subsequent chapters.

<img src="https://www.tutorialspoint.com/nodejs/images/nodejs_concepts.jpg" />

### Where Should I use Node.js?
The following are the areas where Node.js is proving itself as a perfect technology partner.

- I/O bound Applications
- Data Streaming Applications
- Data Intensive Real-time Applications (DIRT)
- JSON APIs based Applications
- Single Page Applications

### Is there a place that I cannot use or not reccomended to use node.js?
It is not advisable to use Node.js for CPU intensive applications.

## Environment Setup

You really do not need to set up your own environment to start learning Node.js. Reason is very simple, we already have set up Node.js environment online, so that you can execute all the available examples online and learn through practice. Feel free to modify any example and check the results with different options.

Here is a following example:

```node
   /* Hello World! program in Node.js */
   console.log("Hello World!");
```

There are many examples given in this tutorial, so just make use of it and enjoy your learning.

### Local Environment Setup
If you are still willing to set up your environment for Node.js, you need the following two softwares available on your computer, (a) Text Editor and (b) The Node.js binary installables.

#### Text Editor
This will be used to type your program. Examples of few editors include Windows Notepad, OS Edit command, Brief, Epsilon, EMACS, and vim or vi.

Name and version of text editor can vary on different operating systems. For example, Notepad will be used on Windows, and vim or vi can be used on windows as well as Linux or UNIX.

The files you create with your editor are called source files and contain program source code. The source files for Node.js programs are typically named with the extension **".js"**.

Before starting your programming, make sure you have one text editor in place and you have enough experience to write a computer program, save it in a file, and finally execute it.

#### The Node.js Runtime
The source code written in source file is simply javascript. The Node.js interpreter will be used to interpret and execute your javascript code.

Node.js distribution comes as a binary installable for SunOS , Linux, Mac OS X, and Windows operating systems with the 32-bit (386) and 64-bit (amd64) x86 processor architectures.

Following section guides you on how to install Node.js binary distribution on various OS.

##### Download Node.js archive
Download latest version of Node.js installable archive file from Node.js Downloads. At the time of writing this tutorial, following are the versions available on different OS.

<table>
    <tbody>
        <tr id="hello">
            <td>OS</td>
            <td>Archive Name</td>
        </tr>
        <tr>
            <td>Windows</td>
            <td>node-v6.3.1-x64.msi</td>
        </tr>
        <tr>
            <td>Linux</td>
            <td>node-v6.3.1-linux-x86.tar.gz</td>
        </tr>
        <tr>
            <td>Mac</td>
            <td>node-v6.3.1-darwin-x86.tar.gz</td>
        </tr>
        <tr>
            <td>SunOS</td>
            <td>node-v6.3.1-sunos-x86.tar.gz</td>
        </tr>
    </tbody>
</table>

###### Installation on UNIX/Linux/Mac OS X, and SunOS
Based on your OS architecture, download and extract the archive node-v6.3.1-**osname**.tar.gz into /tmp, and then finally move extracted files into /usr/local/nodejs directory. For example:

```powershell bash shell tcsh
   $ cd /tmp
   $ wget http://nodejs.org/dist/v6.3.1/node-v6.3.1-linux-x64.tar.gz
   $ tar xvfz node-v6.3.1-linux-x64.tar.gz
   $ mkdir -p /usr/local/nodejs
   $ mv node-v6.3.1-linux-x64/* /usr/local/nodejs
```

Add /usr/local/nodejs/bin to the PATH environment variable.

<table>
    <tr id="hello">
        <td>OS</td>
        <td>Output</td>
    </tr>
    <tr>
        <td>Linux</td>
        <td>export PATH=$PATH:/usr/local/nodejs/bin</td>
    </tr>
    <tr>
        <td>Mac</td>
        <td>export PATH=$PATH:/usr/local/nodejs/bin</td>
    </tr>
    <tr>
        <td>FreeBSD</td>
        <td>export PATH=$PATH:/usr/local/nodejs/bin</td>
    </tr>
</table>

###### Intallation on Windows
Use the MSI file and follow the prompts to install the Node.js. By default, the installer uses the Node.js distribution in C:\Program Files\nodejs. The installer should set the C:\Program Files\nodejs\bin directory in window's PATH environment variable. Restart any open command prompts for the change to take effect.

##### Verify installation: Executing a File
Create a js file named **main.js** on your machine (Windows or Linux) having the following code.

```node
   /* Hello, World! program in node.js */
   console.log("Hello, World!");
```

Now execute main.js file using Node.js interpreter to see the result −

```powershell
   $ node main.js
```

If everything is fine with your installation, this should produce the following result −

` Hello, World! `

# THERE WILL BE MORE SOON
# ...
