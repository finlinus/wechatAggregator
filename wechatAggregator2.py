# -*- coding: utf-8 -*-
"""
wechatAggregator version 0.3.3
Feature: Auto log in to mp.weixin.qq.com and get token with selenium

@author: finn
"""

import argparse
import datetime
import json
import os
import random
import re
import time
import webbrowser

import requests
from selenium import webdriver
from stdiomask import getpass


class Input:
    subscription_file = 'wechat_subscriptions.txt'
    html_file = 'wechat_portal.html'
    timedel = 1
    max_trial = 5
    sort_by_time = True
    update_cookie = True
    add_account = None
    username = ''
    password = ''

class Session:
    token = ''
    cookies = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/64.0'}

class Urls:
    index = 'https://mp.weixin.qq.com'
    query_biz = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    query_arti = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
    
def set_cookies(driver, cookies):
    Session.cookies = {}
    for item in cookies:
        driver.add_cookie(item)
        Session.cookies[item['name']]=item['value']
        
def update_cookies(cookie_file='src/cookies.json', force_update=False):
    driver = webdriver.Firefox(executable_path='C:\\Program Files\\Mozilla Firefox\\geckodriver.exe')
    #driver = webdriver.Chrome(executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe')
    driver.get(Urls.index)
    time.sleep(2)
    cookies = json.load(open(cookie_file, 'rb')) if os.path.isfile(cookie_file) else []
    if cookies == [] or force_update is True:
        if Input.username != '':
            driver.find_element_by_name('account').clear()
            driver.find_element_by_name('account').send_keys(Input.username)
            time.sleep(2)
            driver.find_element_by_name('password').clear()
            driver.find_element_by_name('password').send_keys(Input.password)
            time.sleep(2)
            driver.find_element_by_class_name('btn_login').click()
        input('Please scan the QR code and confirm login on your phone, then hit Enter to continue:')
        cookies = driver.get_cookies()
        open(cookie_file, 'wb').write(json.dumps(cookies).encode('utf-8'))
    set_cookies(driver, cookies)
    driver.get(Urls.index)
    url = driver.current_url
    if 'token' not in url:
        raise Exception(f'Error loading web page, please try again later!')
    else:
        Session.token = re.findall(r'token=(\w+)', url)[0]
        
def search_gzh(query, max_num=None):
    if Session.token == '':
        update_cookies(force_update=Input.update_cookie)
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
    search_response = requests.get(Urls.query_biz, cookies=Session.cookies, headers=Session.headers, params=query_id)
    err_msg = search_response.json()['base_resp']['err_msg']
    lists = search_response.json().get('list', [])    
    if err_msg == 'ok':
        if lists != []:
            fakeid = lists[0].get('fakeid', '')
            subscription = lists[0].get('nickname', '')
            print('Loading [' + subscription + '] with success')
        else:
            print('Loading [' + query + '] with success, but no article available')
            return [], []
    else:
        print('Loading [' + query + '] with error: ' + err_msg)
        return [], []
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
    appmsg_response = requests.get(Urls.query_arti, cookies=Session.cookies, headers=Session.headers, params=query_id_data)
    # fetch more than default
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
            query_fakeid_response = requests.get(Urls.query_arti, cookies=Session.cookies, headers=Session.headers, params=query_id_data)
            fakeid_list = query_fakeid_response.json().get('app_msg_list', '')
            article_list.extend(fakeid_list)
            num -= 1
            begin = int(begin)
            begin += 5     
    return subscription, article_list

def get_gzh_articles(subscription_file='wechat_subscriptions.txt', timedel=2, sort_by_time=True, 
                     max_trial=5, add_account=None):
    '''Get updated articles for your WeChat subscriptions.
    
    Parameters
    --------------------
    subscription_file: str. location of text file which holds your subscriptions
    timedel: int. days to filter most recent articles
    sort_by_time: bool. whether sort articles by time or not
    max_trial: int. max times of trial if there are accounts with no articles returned
    add_account: list or None. update subscription list with given account(s)
    
    Returns
    --------------------
    article_list: articles are held in dicts
    account_nohit: accounts didn't return any article
    '''
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
            subscription, article_list = search_gzh(account)   
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
        print('如不想重复输入，可在config.json文件Method 2下username后引号中填入用户名')
    if Input.password == '':
        Input.password = getpass(prompt='请输入密码: ', mask='*')
        print('如不想重复输入，可在config.json文件Method 2下password后引号中填入密码')
    articles, _nohit = get_gzh_articles(subscription_file=Input.subscription_file, 
                                        timedel=Input.timedel, 
                                        sort_by_time=Input.sort_by_time, 
                                        max_trial=Input.max_trial, 
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
    parser.add_argument('-update_cookie', dest='update_cookie', type=bool, help='whether to update cookie or not, default True')
    parser.add_argument('-add', dest='add_account', nargs='*', help='add subscriptions, default None')
    parser.add_argument('-u', dest='username', type=str, help='try auto login with given username, default ""')
    parser.add_argument('-p', dest='password', type=str, help='try auto login with given password, default ""')
    args = parser.parse_args()
    conf_preset = {'subscription_file': 'wechat_subscriptions.txt', 
                   'html_file': 'wechat_portal.html', 
                   'timedel': 1, 
                   'max_trial': 5, 
                   'sort_by_time': True, 
                   'update_cookie': True, 
                   'add_account': None,
                   'username': '',
                   'password': ''}
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            conf = json.load(f)
            conf = conf['Method 2']['Parameters']
    except:
        conf = conf_preset
    Input.subscription_file = args.subscription_file if args.subscription_file else conf['subscription_file']
    Input.html_file = args.html_file if args.html_file else conf['html_file']
    Input.timedel = args.timedel if args.timedel else conf['timedel']
    Input.max_trial = args.max_trial if args.max_trial else conf['max_trial']
    Input.sort_by_time = args.sort_by_time if args.sort_by_time else conf['sort_by_time']
    Input.update_cookie = args.update_cookie if args.update_cookie else conf['update_cookie']
    Input.add_account = args.add_account if args.add_account else conf['add_account']
    Input.username = args.username if args.username else conf['username']
    Input.password = args.password if args.password else conf['password']
    main()
