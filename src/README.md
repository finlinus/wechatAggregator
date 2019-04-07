wechatAggregator by @finn(finlinus@foxmail.com)

提供两种实现方式：

wechatsogou ---------->wechatAggregator.py[Method 1];

登录个人公众号 -------->wechatAggregator2.py[selenium-based, Method 2],

---------------------->wechatAggregator3.py[requests-based, Method 3]

本程序根据自定义的公众号列表，将这些公众号过去24小时之内发布的内容汇总到一个网页，以应对需要电脑上处理文章的情形。 This program creates a web portal which summarizes activities of all your WeChat subscriptions in last 24 hours.

功能特点：

仅需双击就可以获取所订阅公众号24小时内的内容更新；
有些文章更适合在电脑端浏览器上阅读、标记和保存；
有时候指望拿手机当学习工具是件相当考验人的事；
还有很多，就不一一写了。
使用方法： 程序主要通过config.json（以下称A）和wechat_subscriptions.txt（以下称B）两个文件配置， 同时也接受直接传参，可以使用python [py文件] --help了解更多。 程序输出为wechat_portal.html网页文件（以下称C），并自动调用浏览器打开。 具体地：

在B中填入要获取文章内容的公众号列表，参照提供的示例，一行一个公众号关键词, 对于Method 3，可以打开A将sync_account值由false改为true，通过登录个人微信一步同步关注的公众号，然后根据需要编辑B去掉营销号之类的。 （最好输入公众号全称以保证获取的的文章来自目标公众号；不需要同步时记得将sync_account改回false）
根据方法选择py文件在python中执行以获取文章。 （获取文章需要时间，依赖于公众号列表长度和内容提供商的响应速度，等待期间可以先最小化弹出的运行窗口）
点击文章标题可以转到文章链接，点击文章序号可以隐藏该文章，刷新网页恢复初始化。
注意事项：

方法有可能失效，需要根据生存情况选择。
产生的汇总网页文件（‘wechat_portal.html’）每次运行软件时会被覆盖，如有需要，请先备份该文件；
根据内容提供商的访问控制政策，网页中的各文章链接并不是长久有效的，如有需要，请先做好笔记或将文章保存成pdf等格式。
致谢：

本程序主要受公众号‘Alfred数据室’的原创文章启发，在此对作者表示感谢。
Features:

keep updated with your wechat subscriptions in two clicks;
better readability on PC web browser, and more friendly to taking notes;
cell phones are poisonous;
many more.
Acknowledgement:

this program was inspired by an original article of wechat subscription 'Alfred数据室', I would like to express my gratitude to the author here.
LICENSE AND DISCLAIMER I DEVELOPED THIS PROGRAM WITHOUT COMMERCIAL INTENTION. USERS ARE FREE TO USE AND REDISTRIBUTE THIS PROGRAM. HOWEVER, I WOULD REALLY APPECIATE IT IF THE USERS COULD MAINTAIN INTEGRITY OF THIS README FILE WHEN YOU USE OR REDISTRIBUTE THIS PROGRAM. TECENT INC AND SOGOU.COM HAVE THE RIGHT TO RESTRICT OR BLOCK CONNECTIONS OF THIS PROGRAM, DON'T ABUSE THIS PROGRAM BEYOND YOUR NEED AND LEGAL RISKS ARE AT YOUR OWN.
