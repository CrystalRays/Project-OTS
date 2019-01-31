# Project-OTS

<p align=center><img src="https://upload.cc/i1/2019/01/31/AY5KMD.png" width=600/></p>

<p align="center">Online Exam System written on Python 3. Your can first try it on [ots.icystal.top](https://ots.icystal.top).<br>基于Python 3的在线考试系统。你可以先在[这里](https://ots.icystal.top)体验这个考试系统。</p>

## Function功能

- Create question database and add questions into it.新建题库并向其中添加题目。

- Create and manage accounts for your students.添加并管理你的学生。

- Create and start an online examination.创建并开始一场在线考试。

- Your students could login in and join the exam on the website.学生登录网站并开始考试。

- Auto grade after students finish exam.学生完成考试后自动评分

- ~~Check every student’s  answer and grade in every exam.查看学生的考试成绩（developing...）~~

## Requirement环境需求

    Python 3 with flask, jinja2, pycryptodome 
    
    安装了flask、jinja2和pycryptodome的Python 3

## Usage使用说明

Tip: Following only to introduce the usage in LAN,

        It is similar for Internet use except the servershould be able to be accessed through Internet. 

提示：以下仅以局域网使用为例。互联网使用类似，除了需要一台拥有独立互联网ip或者内网映射过的计算机。

### First time run首次使用

1. Install the requirement upon.安装环境需求

2. Double click the run.py and finish the settings by order.(normally set the port 80)

   双击运行run.py并按照提示完成设置（通常端口设置为80）

3. Visit the website using your ip as url and sign in the administrator account you set on last step.

   在浏览器中访问你的ip地址，用你刚设置的管理员账户登录

<p align=center><img width=600 src="https://upload.cc/i1/2019/01/31/4rVEgw.png" /></p>

### Usage for students学生使用

Login with the account provide by teacher and enter a exam ongoing, click the submit button and wait for grade when finish the exam.

登录老师提供的账号并进入一项正在进行的考试，考试完成后点击右上角提交按钮等待评分即可。

## Autograder评分器

In fact you can modify the autograder.

By default, we provide the "standard"(default) autograder and the "clangcalc"(designed for C programming exam) autograder.

You can write your own autograder with python 3 and use it on the system.

事实上你可以自定义评分器

默认我们提供standard和clangcalc两个评分器，前者是默认评分器，后者是为C语言考试而设计的

你可以用Python 3自己写一个评分器，并在这个系统中使用

### Choose another grader for specific question


Login into your admin account and enter the question database manager and check the question setting. You can change the grader in the textbox next to the question id. If the grader’s .py file is clangcalc.py, you should input clangcalc there.

登录你的管理员账户，进入题库管理，选择一个题库点查看，你可以在每道题题号旁边看到一个用来设置评分器的输入框。如果评分器的.py文件的文件名是clangcalc.py，你就应该在这里填入clangcalc。

![Autograder Setting](https://upload.cc/i1/2019/01/31/PE6hgW.png)

### Write your own grader


The grader‘s .py file should include a function named calc which receive two parameters(the first one is the student's answer and the last is the standard answer) and return a number from 0 to 1 as the correct rate. The .py file should placed on the same folder with run.py.

评分器的.py文件应该包含名为calc的函数作为入口函数，该函数接受两个参数，第一个是学生的答案，第二个是标准答案，并且返回一个≥0且≤1的数作为正答率。这个.py文件应该和run.py放在同一个目录下。

<p align=center><img width = '400'  src ="https://upload.cc/i1/2019/01/31/5Vtqdb.png"/></p>

