import os
import difflib
import re
import time
import json
import xml.etree.cElementTree as ET

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta

GOOGLE_TIME = '%a, %d %b %Y %H:%M:%S UTC'

# download the XML
with open('secret.txt', 'r') as f:
    secret = json.load(f)
    username = secret['gmail']['username']
    password = secret['gmail']['password']

chrome_options = Options()
chrome_options.add_argument("--verbose")
chrome_options.add_argument("user-data-dir=/Users/bgleitzman/projects/TardyParty")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5")
driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)

driver.get(u'http://www.groups.google.com')

driver.implicitly_wait(10)

try:
    elem = driver.find_element_by_id("gb_70")
    elem.click()

    user_field = driver.find_element_by_id('Email')
    user_field.send_keys(username)

    elem = driver.find_element_by_id("next")
    elem.click()

    password_field = driver.find_element_by_id('Passwd')
    password_field.send_keys(password)

    driver.find_element_by_id('signIn').click()

    time.sleep(20)
except NoSuchElementException:
    # already signed in
    pass

driver.get(u'https://groups.google.com/forum/feed/oxidized-bismuth-blogger/topics/rss.xml?num=50')

xml = driver.find_element_by_id('webkit-xml-viewer-source-xml')
xml = xml.get_attribute('innerHTML')

driver.quit()

xml = xml.encode('utf-8')

# with open('rss.xml') as f:
    # xml = f.read()

tree = ET.fromstring(xml)

people = ['dbro', 'Jorin Vogel', 'savannahjune', 'Nicole Ricasata', 'Chris Ballinger', 'Chris Maury', 'Evan Burchard', 'Jam Kotenko', 'Jason Kotenko', 'Rich Jones', 'me', 'Geoff', 'Parker Phinney', 'Chris Christakis', 'Dmitri Sullivan', 'Janet Li', 'Kara Oehler', 'Dan Levine', 'Heather Conover', 'Adrian Winn', 'Andrew Magliozzi', 'George Zisiadis', 'sean.taylorleech', 'Collin Morris', 'Fernandocg', 'Randy Lubin', 'Jeremy Herrman', 'Freenerd', 'folkloregold', 'Katie Johnson', 'wdaher', 'Paul Pollack', 'Katie Broida', 's.d.a.herzog', 'Anthony Ferraro', 'nick', 'Vivek S.', 'Brentan Alexander', 'Ruvan', 'dmitric', 'Ted Seabright', 'Emily Sutton', 'tlcarvalho74', 'Luke Carlson', 'majikman', 'Benjamin Gleitzman', 'Sam Fomon', 'John Shahabian']
# hiatus

now = datetime.now()
monday = now - timedelta(days=(now.weekday()))
# days=8, weekday - 1 if you're running on a tuesday
last_monday = monday - timedelta(days=23)

people_who_wrote = {}

items = tree[0][4:]  # start of messages
name_re = re.compile("\((.*)\)")  # match name inside parens
for item in items:
    item_pubdate = datetime.strptime(item[5].text.strip(), GOOGLE_TIME)
    if item_pubdate > last_monday and item_pubdate < monday:
        if not item[0].text or 'Re:' in item[0].text.strip():
            continue
        clean_name = item[4].text.strip()
        if '(' not in clean_name:
            continue
        name = name_re.search(clean_name).groups()[0]

        if name == 'me':
            name = 'Benjamin Gleitzman'

        info_dict = {}

        if name in people_who_wrote:
            info_dict = {'title': item[0].text.strip(),
                         'url': item[1].text.strip()}
        else:
            canonical_names = difflib.get_close_matches(name, people)
            if canonical_names:
                canonical_name = canonical_names[0]
                people.remove(canonical_name)
                info_dict = {'title': item[0].text.strip(),
                             'url': item[1].text.strip()}

        if info_dict:
            people_who_wrote.setdefault(name, []).append(info_dict)

EMAIL_FORM = u'''
<p>My dearest idea generator,</p>

<p>Here are the standings for the week of {0}. As a reminder, everyone is obliged to post at least one idea before 4:20 AM Monday morning.</p>

<p>This week's most excellent oxbiz bloggers:</p>

<p>{1}</p>

<p>People who need a little motivation:</p>

<p>{2}</p>

<p>Yours,<br/>
Benjamin</p>
'''

last_monday_str = datetime.strftime(last_monday, '%m/%d')

winner_list = []
for name, p in people_who_wrote.items():
    p = p[0]
    winner_list.append(u'<li><img src="https://mail.google.com/mail/e/B60" goomoji="B60" style="margin:0px 0.2ex;vertical-align:middle"> <a href="{0}">{2}</a> - {1}</li>'.format(p['url'], name, p['title']))

loser_list = []
for loser in people:
    loser_list.append('<li><img src="https://mail.google.com/mail/e/1E3" style="margin:0px 0.2ex;vertical-align:middle" goomoji="1E3"> <a href="{}">{}</a></li>'.format('https://dl.dropbox.com/u/101688/website/mp3/sad.mp3', loser))

winners = '<ul>' + '\n'.join(winner_list) + '</ul>'
losers = '<ul>' + '\n'.join(loser_list) + '</ul>'
email_str = EMAIL_FORM.format(last_monday_str, winners, losers)

f = open('/tmp/oxbiz.html', 'w')
email_str = email_str.encode('utf-8')
f.write(email_str)
f.close()

os.system('open /tmp/oxbiz.html')

print email_str
print 'People who wrote are', ', '.join(people_who_wrote.keys())
print 'People who didn\'t write are', ', '.join(people)
