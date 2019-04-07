# -*- coding: utf-8 -*-
'''
wechatAggregator version 0.3.3
Feature: Auto log in to mp.weixin.qq.com and get token with requests

@author: finn
''' 
import argparse
import datetime
import hashlib
import json
import os
import random
from stdiomask import getpass
import time
import webbrowser
import itchat

import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable insecure warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Input:
    subscription_file = 'wechat_subscriptions.txt'
    html_file = 'wechat_portal.html'
    timedel = 1
    max_trial = 5
    sort_by_time = True
    sync_account = False
    add_account = None
    username = ''
    password = ''

class Urls:
    base_url = 'https://mp.weixin.qq.com'
    login_url = 'https://mp.weixin.qq.com/cgi-bin/bizlogin'
    qr_url = 'https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=getqrcode'
    qr_status = 'https://mp.weixin.qq.com/cgi-bin/loginqrcode'
    query_biz = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    query_arti = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'

class Session:
    headers = {
    'accept-encoding': "gzip, deflate, sdch, br", 
    'accept-language': "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4", 
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/64.0", 
    'accept': "*/*", 
    'x-requested-with': "XMLHttpRequest", 
    'connection': "keep-alive", 
    'cache-control': "no-cache", 
    'referer': 'https://mp.weixin.qq.com/'
    } 
    token = ''

def to_md5(test):
    '''for converting password to md5.'''
    if not isinstance(test, bytes):
        test = bytes(test, 'utf-8')
    m = hashlib.md5()
    m.update(test)
    return m.hexdigest()

def get_token(session):
    '''Get session token.'''
    # gzh login
    session.request("GET", Urls.base_url, headers=Session.headers, verify=False) 
    querystring = {"action": "startlogin"}
    payload = "username=" + Input.username + "&pwd=" + Input.password + "&imgcode=&f=json&userlang=zh_CN&token=&lang=zh_CN&ajax=1" 
    response = session.request("POST", Urls.login_url, data=payload, headers=Session.headers, params=querystring, verify=False) 
    content = response.text 
    redirect_url = Urls.base_url + json.loads(content)['redirect_url']
    # get qr code
    session.request("GET", redirect_url, headers=Session.headers) 
    qr_code = session.get(Urls.qr_url) 
    with open('src/login.jpg', 'wb') as f:
        f.write(qr_code.content) 
    os.startfile(os.path.abspath('src/login.jpg'))
    # check status
    while True: 
        querystring = {"action": "ask", "token": "", "lang": "zh_CN", "f": "json", "ajax": "1"} 
        response = session.request("GET", Urls.qr_status, headers=Session.headers, params=querystring) 
        content = response.text
        status = json.loads(content)['status']
        if status == 1:
            print('登录成功！')
            os.system(r'taskkill /f /fi "WINDOWTITLE eq Photos*" /t')
            break
        elif status == 0:
            print('请用微信扫描二维码')
        else:
            print('已扫描，请继续点确认')
        time.sleep(2) 
    # final_login:
    querystring = {"action": "login"} 
    payload = "token=&lang=zh_CN&f=json&ajax=1" 
    response = session.request("POST", Urls.login_url, data=payload, headers=Session.headers, params=querystring, verify=False) 
    content = response.text 
    redirect_url = Urls.base_url + json.loads(content)['redirect_url'] 
    session.request("GET", redirect_url, headers=Session.headers, verify=False) 
    arr = redirect_url.split('=') 
    Session.token = arr[-1]

def search_gzh(session, query, max_num=None):
    '''search gzh by query name.
    --------------------
    Parameters:
        session: requests session to start searching
        query: str. subscription name to search
        max_num: int, default None. max number of articles to retrieve.
        
    --------------------
    Returns:
        subscription: [str]. list of subscription(s) that matches/match input query
        article_list: list of articles
        exit_flag: bool. abort excution if server freq control triggered
    '''
    query_id = {
        'action': 'search_biz',
        'token' : Session.token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': query,
        'begin': '0',
        'count': '5',
    }
    search_response = session.get(Urls.query_biz, headers=Session.headers, params=query_id)
    err_msg = search_response.json()['base_resp']['err_msg']
    lists = search_response.json().get('list', [])
    exit_flag = False
    try:
        fakeid = lists[0].get('fakeid', '')
        subscription = lists[0].get('nickname', '')
        print('Loading [' + subscription + '] with success')
        query_id_data = {
            'token': Session.token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '0',
            'count': '5',
            'query': '',
            'fakeid': fakeid,
            'type': '9'
        }
        appmsg_response = session.get(Urls.query_arti, headers=Session.headers, params=query_id_data)
        if max_num is None:
            article_list = appmsg_response.json().get('app_msg_list', [])
        else:
            max_num = min(max_num, appmsg_response.json().get('app_msg_cnt'))
            article_list = []
            num = int(int(max_num) / 5)
            begin = 0
            while num + 1 > 0 :
                query_id_data = {
                    'token': Session.token,
                    'lang': 'zh_CN',
                    'f': 'json',
                    'ajax': '1',
                    'random': random.random(),
                    'action': 'list_ex',
                    'begin': '{}'.format(str(begin)),
                    'count': '5',
                    'query': '',
                    'fakeid': fakeid,
                    'type': '9'
                }
                query_fakeid_response = session.get(Urls.query_arti, headers=Session.headers, params=query_id_data)
                fakeid_list = query_fakeid_response.json().get('app_msg_list', '')
                article_list.extend(fakeid_list)
                num -= 1
                begin = int(begin)
                begin += 5     
        return subscription, article_list, exit_flag
    except:
        print('Loading [' + query + '] with error: ' + err_msg)
        exit_flag = True
        return [], [], exit_flag

def get_gzh_articles(session, subscription_file='wechat_subscriptions.txt', timedel=2, sort_by_time=True, 
                     max_trial=5, sync_account=False, add_account=None):
    '''Get updated articles for your WeChat subscriptions.
    
    Parameters
    --------------------
    sync_account: bool, default False. sync subscriptions to your wechat account
    timedel: int. days to filter most recent articles
    sort_by_time: bool. whether sort articles by time or not
    max_trial: int. max times of trial if there are accounts with no articles returned
    add_account: list or None. update subscription list with given account(s)
    
    Returns
    --------------------
    article_list: articles are held in dicts
    account_nohit: accounts didn't return any article
    '''
    subscription_file='wechat_subscriptions.txt'
    if sync_account:
        itchat.login()
        mps = itchat.get_mps(update=True)
        mps_name = [mp['NickName'] for mp in mps]
        mps_name = '\n'.join(mps_name)
        with open(subscription_file, 'w', encoding='utf-8-sig') as f:
            f.write(mps_name)
        itchat.logout()
    with open(subscription_file, 'r', encoding='utf-8-sig') as f: # handle BOM on Windows
       accounts = [account.strip() for account in f.readlines() if account != '\n']
    # add accounts
    if add_account is not None:
        for new_account in add_account: 
            if new_account not in accounts:
                accounts.append(new_account)
                with open(subscription_file, 'a', encoding='utf8') as f:
                    f.write(new_account + '\n')
            else:
                print('Got duplicate account: ' + new_account)
    # fetch articles
    articles, epoch = [], 0
    while len(accounts) > 0 and epoch < max_trial:
        for account in accounts:
            subscription, article_list, exit_flag = search_gzh(session, account, max_num=None)
            if exit_flag:
                break
            if article_list != list():
                accounts.remove(account)
                for article_ in article_list:
                    article_['Account name'] = subscription
                articles.extend(article_list)
            time.sleep(8)
        epoch += 1
        if epoch < max_trial - 1:
            time.sleep(60)
    
    if articles == list():
        return [], accounts

    # filter time
    if len(articles) > 0:
        timestamp = int((datetime.datetime.now()-datetime.timedelta(days=timedel)).timestamp())
        articles = [article for article in articles if article['update_time'] > timestamp]
    # Final formatting
    # sort by time
    if sort_by_time:
        articles = sorted(articles, key=lambda x: x['update_time'], reverse=True)
    articles_ = []
    for article in articles:
        time_str = datetime.datetime.fromtimestamp(article['update_time']).ctime()
        articles_.extend([{'Title': article['title'], 'Abstract': article['digest'], 
                           'Account name': article['Account name'], 'Publication time': time_str, 
                           'url': article['link']}])
    return articles_, accounts

def to_html(articles, account_nohit=list(), html_file='wechat_portal.html'):
    '''HTML for enhanced readability.
    --------------------
    Parameters:
        articles: list. article list.
        account_nohit: list. a list of accounts didn't return any articles.
        html_file: str. file name of HTML
    '''
    html_header = ['<!DOCTYPE HTML>', '<html>', '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />', 
                   '<head>', '<title>Wechat Portal</title>', '<link rel="stylesheet" type="text/css" href="src/mystyle.css">', 
                   '</head>', '<body>', '<div id="headlinks">', '<a href="src/README.md" target="_blank">About</a>&nbsp&nbsp&nbsp', 
                   '<a href="mailto:finlinus@foxmail.com?Subject=Hello,..." target="_top">Contact</a>', 
                   '</div>', '<div id="welcome"><div id="intro">', '<h1>WELCOME</h1>', 
                   '<h2>Below are most recent activities of your WeChat subsciptions.</h2>', '</div></div></header>', 
                   '<table>', '<script>', 'function DeleteRow(o){', 'var p=o.parentNode.parentNode;', 
                   'p.parentNode.removeChild(p);', '}', '</script>', '<colgroup>', '<col style="width:3%">', 
                   '<col style="width:26%">', '<col style="width:41%">', '<col style="width:15%">', '<col style="width:15%">', 
                   '</colgroup>', '<tbody>', '<tr>', '<th>No.</th>', '<th>Title</th>', '<th>Abstract</th>', 
                   '<th>Subscription Name</th>', '<th>Publication Time</th>', '</tr>']
    html_body = []
    for i, article in enumerate(articles, start=1):
        html_body.extend(['''<tr>\n<td><button onclick="DeleteRow(this)">%i</button></td>\n<td><a href=%s target="_blank">%s</a></td>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td></tr>\n''' % 
                              (i, article['url'], article['Title'], article['Abstract'], article['Account name'], article['Publication time'])])
    if account_nohit == list():
        html_footer = ['</tbody>', '</table>', '</body>', '</html>']
    else:
        nohit_ = '<h4>' + ', '.join(account_nohit) + '</h4>'
        warning_ = ['<div id="footer"><h3>These subscriptions did NOT return any article:</h3>', nohit_, 
                    '<p>If this is not normal, please recheck names of these subscriptions in file wechat_subscriptions.txt.</p>', 
                    '<p>If problem persists, feel free to contact <a href="mailto:finlinus@foxmail.com?Subject=Hello,..." target="_top">me</a>.</p>']
        html_footer = ['</tbody>', '</table><hr>']
        html_footer.extend(warning_)
        html_footer.extend(['</div></body>', '</html>'])
    with open(html_file, 'w', encoding='utf8') as f:
        f.write('\n'.join(html_header))
        for artc in html_body:
            f.write(artc)
        f.write('\n'.join(html_footer))
    webbrowser.open_new_tab(os.path.abspath(html_file))

def main():
    if Input.username == '':
        Input.username = input('请输入公众号用户名: ')
        print('如不想重复输入，可在config.json文件Method 3下username后引号中填入用户名')
    if Input.password == '':
        password = getpass(prompt='请输入密码: ', mask='*')
        Input.password = to_md5(password)
        print('如不想重复输入，可在config.json文件Method 3下password后引号中填入密码的md5值: ' + Input.password)
    session = requests.Session()
    if Session.token == '':
        get_token(session)
    articles, _nohit = get_gzh_articles(session, 
                                        subscription_file=Input.subscription_file, 
                                        timedel=Input.timedel, 
                                        sort_by_time=Input.sort_by_time, 
                                        max_trial=Input.max_trial, 
                                        sync_account=Input.sync_account, 
                                        add_account=Input.add_account)
    to_html(articles, account_nohit=_nohit, html_file=Input.html_file)
    
if __name__ == '__main__':
    description = u'Update most recent activities of your wechat subscriptions'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-subscription_file', dest='subscription_file', type=str, help='subscription text file, default "wechat_subscription.txt"')
    parser.add_argument('-html_file', dest='html_file', type=str, help='html file, default "wechat_portal.html"')
    parser.add_argument('-timedel', dest='timedel', type=int, help='this specifies how many days to update, default 1')
    parser.add_argument('-max_trial', dest='max_trial', type=int, help='times of trials until all articles acquired successfully')
    parser.add_argument('-sort', dest='sort_by_time', type=bool, help='whether to sort articles by time or not, default True')
    parser.add_argument('-sync', dest='sync_account', type=bool, help='whether to sync subscriptions to wechat account, default False.')
    parser.add_argument('-add', dest='add_account', nargs='*', help='add subscriptions, default None')
    parser.add_argument('-u', dest='username', type=str, help='try auto login with given username, default ""')
    parser.add_argument('-p', dest='password', type=str, help='try auto login with given password, default ""')
    args = parser.parse_args()
    conf_preset = {'subscription_file': 'wechat_subscriptions.txt', 
                   'html_file': 'wechat_portal.html', 
                   'timedel': 1, 
                   'max_trial': 5, 
                   'sort_by_time': True,
                   'sync_account': False, 
                   'add_account': None,
                   'username': '',
                   'password': ''
    }
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            conf = json.load(f)
            conf = conf['Method 3']['Parameters']
    except:
        conf = conf_preset
    Input.subscription_file = args.subscription_file if args.subscription_file else conf['subscription_file']
    Input.html_file = args.html_file if args.html_file else conf['html_file']
    Input.timedel = args.timedel if args.timedel else conf['timedel']
    Input.max_trial = args.max_trial if args.max_trial else conf['max_trial']
    Input.sort_by_time = args.sort_by_time if args.sort_by_time else conf['sort_by_time']
    Input.sync_account = args.sync_account if args.sync_account else conf['sync_account']
    Input.add_account = args.add_account if args.add_account else conf['add_account']
    Input.username = args.username if args.username else conf['username']
    Input.password = args.password if args.password else conf['password']
    main()
