wechatAggregator by @finn(finlinus@foxmail.com)
(本开放版不集成自动识别图片验证码功能。No OCR integrated in this version.)

本程序根据自定义的公众号列表，将这些公众号过去24小时之内发布的内容汇总到一个网页，以应对需要电脑上处理文章的情形。
This program creates a web portal which summarizes activities of all your WeChat subscriptions in last 24 hours.

功能特点：
1. 仅需双击就可以获取所订阅公众号24小时内的内容更新；
2. 有些文章更适合在电脑端浏览器上阅读、标记和保存；
3. 有时候指望拿手机当学习工具是件相当考验人的事；
4. 还有很多，就不一一写了。

使用方法：
1. 解压到任意位置后在'wechat_subscriptions.txt'中填入要获取文章内容的公众号列表，参照提供的示例，一行一个公众号关键词；
  （最好输入公众号全称以保证获取的的文章来自目标公众号）
2. 运行'wechatAggregator_.exe'，将产生一个汇总网页，并自动调用系统默认浏览器打开，
   如果不慎关掉了该网页，请到文件夹中找到‘wechat_portal.html’文件手动在浏览器中打开，
   也可以添加到浏览器书签，挪动了文件位置之后需要重新添加书签；
  （获取文章需要时间，依赖于公众号列表长度和内容提供商的响应速度，等待期间可以先最小化弹出的运行窗口）
3. 点击文章标题可以转到文章链接，点击文章序号可以隐藏该文章，刷新网页恢复初始化；
4. 有些时候因为内容提供方的访问控制机制会需要输入图片验证码，请先记好验证码，然后关掉弹出的图片查看器，最后在提示里填入验证码并按回车。
   (频繁运行软件可能导致暂时被内容提供商的访问控制机制拒绝访问，此时请若干小时后再试)

注意事项：
1. 只需要编辑'wechat_subscriptions.txt'中的内容，其它文件请保持原样；
2. 产生的汇总网页文件（‘wechat_portal.html’）每次运行软件时会被覆盖，如有需要，请先备份该文件；
3. 根据内容提供商的访问控制政策，网页中的各文章链接并不是长久有效的，如有需要，请先做好笔记或将文章保存成pdf等格式。

致谢：
1. 本程序主要受公众号‘Alfred数据室’的原创文章启发，在此对作者表示感谢。

-----------------------------------------------------------------------------------------------------------------------------
Features:
1. keep updated with your wechat subscriptions in two clicks;
2. better readability on PC web browser, and more friendly to taking notes;
3. cell phones are poisonous;
4. many more.

How to use:
1. 'wechat_subscriptions.txt' holds your WeChat subscription information, 
   you may need to edit this file to add or modify subscriptions for your own scenarios, 
   and place each subscription line by line;
2. execute 'wechatAggregator_.exe' and a webpage named 'wechat_portal.html' will be created;
3. all done. the webpage will be automatively opened by your default web browser.
   if you accidently closed the webpage, navigate to the program folder and reopen 'wechat_portal.html' manually. 
   
Notices: 
1. edit 'wechat_subscriptions.txt' only; 
2. 'wechat_portal.html' will be overwrited every time you execute 'wechatAggregator_.exe', 
   backup the html file before execution if you need it for further reference;
3. article links will NOT persist for long according to policies of WeChat and Sogou;
4. you may be locked out by Sogou, who offers entrance into WeChat for this program, because of frequent robotic behaviors. 
   in this instance, you may have to wait for a while before retrying.

Acknowledgement:
1. this program was inspired by an original article of wechat subscription 'Alfred数据室', I would like to express my gratitude to the author here.

LICENSE AND DISCLAIMER
I DEVELOPED THIS PROGRAM WITHOUT COMMERCIAL INTENTION. USERS ARE FREE TO USE AND REDISTRIBUTE THIS PROGRAM.
HOWEVER, I WOULD REALLY APPECIATE IT IF THE USERS COULD MAINTAIN INTEGRITY OF THIS README FILE WHEN YOU USE OR REDISTRIBUTE THIS PROGRAM.
TECENT INC AND SOGOU.COM HAVE THE RIGHT TO RESTRICT OR BLOCK CONNECTIONS OF THIS PROGRAM, DON'T ABUSE THIS PROGRAM BEYOND YOUR NEED AND LEGAL RISKS ARE AT YOUR OWN.
