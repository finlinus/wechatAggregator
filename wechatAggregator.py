# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 13:40:36 2019

@author: finn
"""

import datetime
import wechatsogou
import webbrowser
import os.path
import werkzeug.exceptions # pyinstaller doesn't include this module

def gzh_update(subscription_file='wechat_subscriptions.txt', headline=False, original=False, timedel=1, add_account=None):
    '''Get updated articles for your WeChat subscriptions.
    
    Parameters
    --------------------
    subscription_file: str. location of text file which holds your subscriptions
    headline: bool. filter headlines
    original: bool. filter origins
    timedel: int. days to filter most recent articles
    add_account: list or None. update subscription list with given account(s)
    
    Returns
    --------------------
    article list: articles are held in dicts
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
                contents_ = ws_api.get_gzh_article_by_history(keyword=account)
            except:
                contents_ = dict()    
            if contents_ != dict():
                articles_ = contents_['article']
                for article_ in articles_:
                    article_['Account name'] = contents_['gzh']['wechat_name']
                articles.extend(articles_)
            else:
                account_nohit.append(account)
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
    
def main():
    articles, _nohit = gzh_update(subscription_file='wechat_subscriptions.txt', 
                                  headline=False, original=False, timedel=1, add_account=None)
    to_html(articles, account_nohit=_nohit, html_file='wechat_portal.html')
    
if __name__ == '__main__':
    main()
