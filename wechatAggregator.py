# -*- coding: utf-8 -*-
"""
Get wechat subscription articles, version 0.1 (via wechatsogou).
Created on Wed Feb 13 13:40:36 2019

@author: finn
"""

import datetime
import time
import wechatsogou
import webbrowser
import os.path
from hashlib import md5
import requests
import argparse
import json
import werkzeug.exceptions # pyinstaller doesn't include this module

class Input():
    subscription_file = 'wechat_subscriptions.txt'
    html_file = 'wechat_portal.html'
    headline = False
    original = False
    timedel = 1
    sort_by_time = True
    add_account = None

def gzh_update(subscription_file='wechat_subscriptions.txt', headline=False, original=False, 
               timedel=1, sort_by_time=True, add_account=None):
    '''Get updated articles for your WeChat subscriptions.
    
    Parameters
    --------------------
    subscription_file: str. location of text file which holds your subscriptions
    headline: bool. filter headlines
    original: bool. filter origins
    timedel: int. days to filter most recent articles
    sort_by_time: bool. whether sort articles by time or not
    add_account: list or None. update subscription list with given account(s)
    
    Returns
    --------------------
    article_list: articles are held in dicts
    account_nohit: accounts didn't return any article
    '''
    with open(subscription_file, 'r', encoding='utf8') as f:
       accounts = [account.strip() for account in f.readlines()]
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
    articles, account_nohit = [], []
    if len(accounts) > 0:
        ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)
        for account in accounts:
            try:
                # to use ruokuai OCR, modify line 172 first
                contents_ = ws_api.get_gzh_article_by_history(keyword=account, 
                                                      identify_image_callback_sogou=identify_image_callback_ruokuai_sogou, 
                                                      identify_image_callback_weixin=identify_image_callback_ruokuai_weixin)
            except:
                contents_ = dict()    
            if contents_ != dict():
                print('Loading [' + contents_['gzh']['wechat_name'] + '] with success')
                articles_ = contents_['article']
                for article_ in articles_:
                    article_['Account name'] = contents_['gzh']['wechat_name']
                articles.extend(articles_)
            else:
                print('No article returned from [' + account + ']')
                account_nohit.append(account)
            time.sleep(2)
    else:
        articles = []
    # filter time
    if len(articles) > 0:
        timestamp = int((datetime.datetime.now()-datetime.timedelta(days=timedel)).timestamp())
        articles = [article for article in articles if article['datetime'] > timestamp]
    # filter headlines
    if headline and len(articles) > 0:
        articles = [article for article in articles if article['main'] == 1]
    # filter origins
    if original and len(articles) > 0:
        articles = [article for article in articles if article['copyright_stat'] == 100]        
    # Final formatting
    # sort by time
    if sort_by_time:
        articles = sorted(articles, key=lambda x: x['datetime'], reverse=True)
    articles_ = []
    for article in articles:
        time_str = datetime.datetime.fromtimestamp(article['datetime']).ctime()
        articles_.extend([{'Title': article['title'], 'Abstract': article['abstract'], 
                           'Account name': article['Account name'], 'Publication time': time_str, 
                           'url': article['content_url']}])
    return articles_, account_nohit
        
def to_html(articles, account_nohit=list(), html_file='wechat_portal.html'):
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
    
class RClient(object):
    def __init__(self, username, password, soft_id, soft_key):
        self.base_params = {
            'username': username,
            'password': md5(password.encode('utf-8')).hexdigest(),
            'softid': soft_id,
            'softkey': soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        return r.json()

    def rk_report_error(self, im_id):
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()
    
def __identify_image_callback(img, code):
    try:
        # replace certain items with valid ones
        rc = RClient('username', 'password', soft_id, 'soft_key')
        result = rc.rk_create(img, code)
        print('Verification code：', result['Result'])
        return result['Result']
    except Exception:
        raise Exception('Verification error!')

def identify_image_callback_ruokuai_sogou(img):
    return __identify_image_callback(img, 3040) # 3040 or 3000

def identify_image_callback_ruokuai_weixin(img):
    return __identify_image_callback(img, 3060) # 3060 or 3000

def main():
    articles, _nohit = gzh_update(subscription_file=Input.subscription_file, 
                                  headline=Input.headline, 
                                  original=Input.original, 
                                  timedel=Input.timedel, 
                                  sort_by_time=Input.sort_by_time, 
                                  add_account=Input.add_account)
    to_html(articles, account_nohit=_nohit, html_file=Input.html_file)
    
if __name__ == '__main__':
    description = u'Update most recent activities of your wechat subscriptions'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-subscription_file', dest='subscription_file', type=str, help='subscription text, default "wechat_subscription.txt"')
    parser.add_argument('-html_file', dest='html_file', type=str, help='html file, default "wechat_portal.html"')
    parser.add_argument('-timedel', dest='timedel', type=int, help='this specifies how many days to update, default 1')
    parser.add_argument('-headline', dest='headline', type=bool, help='only show headline articles, default False')
    parser.add_argument('-sort_by_time', dest='sort_by_time', type=bool, help='whether to sort articles by time or not, default True')
    parser.add_argument('-original', dest='original', type=bool, help='only show original articles, default False')
    parser.add_argument('-add_account', dest='add_account', nargs='*', help='add subscriptions, default None')
    args = parser.parse_args()
    conf_preset = {'subscription_file': 'wechat_subscriptions.txt', 
                   'html_file': 'wechat_portal.html', 
                   'timedel': 1, 
                   'headline': False,
                   'original': False,
                   'sort_by_time': True, 
                   'add_account': None}
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            conf = json.load(f)
            conf = conf['Method 1']['Parameters']
    except:
        conf = conf_preset
    Input.subscription_file = args.subscription_file if args.subscription_file else conf['subscription_file']
    Input.html_file = args.html_file if args.html_file else conf['html_file']
    Input.timedel = args.timedel if args.timedel else conf['timedel']
    Input.headline = args.headline if args.headline else conf['headline']
    Input.sort_by_time = args.sort_by_time if args.sort_by_time else conf['sort_by_time']
    Input.original = args.original if args.original else conf['original']
    Input.add_account = args.add_account if args.add_account else conf['add_account']
    main()
