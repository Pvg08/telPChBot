import sys
import time
import re
import random
import webbrowser
import configparser
import pyautogui

from pyquery import PyQuery as pq

from telethon import utils, events, TelegramClient, ConnectionMode
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import InputChannel, PeerChat
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.messages import CheckChatInviteRequest
from telethon.extensions import markdown

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException   
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.remote.command import Command
from selenium.webdriver.chrome.options import Options

def wait_between(a,b):
    rand=random.uniform(a, b)
    time.sleep(rand)

def isCryptoBotUrl(url):
    url_res_t0 = re.findall("(?P<url>https?://telegram.me/[^\s()]+_CHANGE_BOT[^\s()]+)", url)
    if url_res_t0:
        return True
    return False

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def dimention(driver):
    d = int(driver.find_element_by_xpath('//div[@id="rc-imageselect-target"]/table').get_attribute("class")[-1])
    return d if d else 3

def solve_images(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "rc-imageselect-target"))
    )
    dim = dimention(driver)
    # ****************** check if there is a clicked tile ******************
    if check_exists_by_xpath(
            driver,
            '//div[@id="rc-imageselect-target"]/table/tbody/tr/td[@class="rc-imageselect-tileselected"]'):
        rand2 = 0
    else:
        rand2 = 1

    # wait before click on tiles
    wait_between(0.5, 1.0)
    # ****************** click on a tile ******************
    tile1 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(
            random.randint(1, dim), random.randint(1, dim))))
    )
    tile1.click()
    if (rand2):
        try:
            driver.find_element_by_xpath(
                '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(random.randint(1, dim),
                                                                                        random.randint(1, dim))).click()
        except NoSuchElementException:
            print('\n\r No Such Element Exception for finding 2nd tile')

    # ****************** click on submit buttion ******************
    driver.find_element_by_id("recaptcha-verify-button").click()

def captchaForm(client, url, password):

    global pos_changed

    do_try_solve_images = False
    do_cb_click = not pos_changed
    do_wait_solve_images = pos_changed

    do_use_proxy = False
    proxy_ip_addr = '193.106.94.118'
    proxy_port = '3128'

    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")

    if (do_use_proxy):
        prox = Proxy()
        prox.proxy_type = ProxyType.MANUAL
        prox.http_proxy = proxy_ip_addr + ":" + proxy_port
        prox.socks_proxy = proxy_ip_addr + ":" + proxy_port
        prox.ssl_proxy = proxy_ip_addr + ":" + proxy_port
        capabilities = webdriver.DesiredCapabilities.CHROME
        prox.add_to_capabilities(capabilities)
        driver = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities = capabilities)
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options)

    try:
        driver.get(url)

        if password:
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'form input[name="paswd"]'))
                )
                EditPassw = driver.find_element_by_css_selector('form input[name="paswd"]')
                if EditPassw:
                    EditPassw.send_keys(password)
                    wait_between(0.1, 0.2)
                    EditPassw.submit()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
                    )
            except:
                EditPassw = False

        wait_between(0.1, 0.3)

        mainWin = driver.current_window_handle

        if do_cb_click:
            try:
                mainFrame = driver.find_elements_by_tag_name("iframe")
                mainFrame = mainFrame[0]
            except:
                return
            ActionChains(driver).move_to_element_with_offset(mainFrame, random.uniform(8, 125),random.uniform(3, 75)).perform()
            driver.switch_to.frame(mainFrame)
            CheckBox = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID ,"recaptcha-anchor"))
            )
            wait_between(0.1, 0.3)
            ActionChains(driver).move_to_element_with_offset(CheckBox, random.uniform(8, 25), random.uniform(3, 25)).pause(random.uniform(0.05, 0.5)).click().perform()
            driver.switch_to.window(mainWin)

        if do_try_solve_images:
            i = 1
            while i < 130:
                print('\n\r{0}-th loop'.format(i))
                # ******** check if checkbox is checked at the 1st frame ***********
                driver.switch_to.window(mainWin)
                WebDriverWait(driver, 10).until(
                    EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe'))
                )
                wait_between(1.0, 2.0)
                if check_exists_by_xpath(driver, '//span[@aria-checked="true"]'):
                    break

                driver.switch_to.window(mainWin)
                # ********** To the second frame to solve pictures *************
                wait_between(0.3, 1.5)
                driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[1])
                solve_images(driver)
                i = i + 1
        else:
            if do_wait_solve_images:
                driver.switch_to.frame(driver.find_elements_by_tag_name("iframe")[0])
                WebDriverWait(driver, 960).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".recaptcha-checkbox-checked"))
                )
                driver.switch_to.window(mainWin)
            wait_between(0.6, 0.8)

        cur_url = driver.current_url

        try:
            SubmitElem = driver.find_element_by_css_selector('form')
            SubmitElem.submit()
        except:
            print("BOT NOT Found: " + driver.current_url)
            return

        WebDriverWait(driver, 500).until(EC.url_changes(cur_url))
        wait_between(0.1, 0.3)

        if driver.current_url != cur_url:
            if not isCryptoBotUrl(driver.current_url):
                cur_url = driver.current_url
                wait_between(0.3, 0.5)
                if isCryptoBotUrl(driver.current_url):
                    print("Found BOT: " + driver.current_url)
                    botStart(client, driver.current_url)
                else:
                    print("BOT NOT Found: " + driver.current_url)
            else:
                print("Found BOT: " + driver.current_url)
                botStart(client, driver.current_url)
        else:
            print("BOT NOT Found: " + driver.current_url)

    finally:
        driver.delete_all_cookies()
        driver.quit()


def botStart(client, url):
    p = re.compile('https?://telegram.me/(BTC_CHANGE_BOT|ETH_CHANGE_BOT)\?start=([0-9a-zA-Z]+)')
    m = p.match(url)
    if m.group(2):
        client.send_message(m.group(1), '/start ' + m.group(2))

def linkCheck(url, doopen, client, deep):
    filematch = getFirstMatch(r"http://telegra.ph/file/([a-z0-9]+.[a-z0-9]+)", url)
    if filematch:
        print("Not checking file " + url)
        return

    print("Checking " + url)
    d = pq(url=url)

    p = d('a[href^="https://telegram.me/BTC_CHANGE_BOT"]:first,a[href^="https://telegram.me/ETH_CHANGE_BOT"]:first')
    if p.length > 0:
        aim = p.attr('href')
        print("Found BOT: " + aim)
        if (doopen):
            botStart(client, aim)
        return

    p = d('form .g-recaptcha')
    if p.length > 0:
        print("Found captcha: " + url)
        if (doopen):
            #captchaForm(client, url, '')
            webbrowser.open(url, 1, True)
        return

    if deep < 3:
        p = d('a[href^="http://raketa8.ru/"][rel!="home"]:first')
        if p.length > 0:
            aim = p.attr('href')
            linkCheck(aim, doopen, client, deep+1)

def getFirstMatch(regex, txt):
    matches = re.finditer(regex, txt, re.UNICODE | re.IGNORECASE)
    for matchNum, match in enumerate(matches):
        for groupNum in range(0, len(match.groups())):
            return match.group(1)
    return False

def textCheck(txt, doopen, delay_s, client):
    print("______________________________________")

    if (txt is None) or (txt == ''):
        return

    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    txt = txt.translate(non_bmp_map)
    print(txt)
    print("______________________________________")

    url_res_t = re.findall("(?P<url>https?://telegram.me/[^\s()]+_CHANGE_BOT[^\s()]+)", txt)
    if url_res_t:
        random.shuffle(url_res_t)
        for url in url_res_t:
            print("Found BOT: " + url)
            if (doopen):
                botStart(client, url)
            time.sleep(delay_s)

    url_res_t = re.findall("(?P<url>http?://raketa8.ru/[^\s()]+)", txt)
    if url_res_t:
        random.shuffle(url_res_t)

        password = getFirstMatch(r"парол[а-я]+ +([a-z0-9]{4,10})", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+[ :]+([a-z0-9]{4,10})", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+ +для +[а-я:]+ +([a-z0-9]{4,10})", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+ +от +[а-я:]+ +([a-z0-9]{4,10})", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+ +\*\*([a-z0-9]{4,10})\*\*", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+[ :\*]+([a-z0-9]{4,10})", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+ +для +[а-я:]+ +\*\*([a-z0-9]{4,10})\*\*", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+ +от +[а-я:]+ +\*\*([a-z0-9]{4,10})\*\*", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я]+[-а-я :]+ +\*\*([a-z0-9]{4,10})\*\*", txt)
        if not password:
            password = getFirstMatch(r"парол[а-я :*]+([a-z0-9]{4,10})", txt)

        if password:
            print("Found captcha password: " + password)

        for url in url_res_t:
            print("Found captcha: " + url)
            if (doopen):
                webbrowser.open(url+"?paswd="+password, 1, True)
                #captchaForm(client, url, password)
            #linkCheck(url, doopen, client, 0)
            time.sleep(delay_s)

    url_res_t = re.findall("(?P<url>http?://telegra.ph/[^\s()]+)", txt)
    if url_res_t:
        random.shuffle(url_res_t)
        for url in url_res_t:
            linkCheck(url, doopen, client, 0)
            time.sleep(delay_s)

def checkCurChat(chatname, client):
    print("\n")

    try:
        int_chat = int(chatname)
    except:
        int_chat = 0

    if int_chat != 0:
        input_channel =  client(GetFullChannelRequest(int_chat))
        channel_id = input_channel.full_chat.id
        print("<<<Fast checking: " + input_channel.chats[0].title + " (" + str(int_chat) + ">>>")
    else:
        response = client.invoke(ResolveUsernameRequest(chatname))
        channel_id = response.peer.channel_id
        print("<<<Fast checking: " + response.chats[0].title + " (" + response.chats[0].username + ") >>>")

    for msg in client.get_messages(channel_id, limit=1):
        if (msg != '') and not (msg is None):
            if not hasattr(msg, 'text'):
                msg.text = None
            if msg.text is None and hasattr(msg, 'entities'):
                msg.text = markdown.unparse(msg.message, msg.entities or [])
            if msg.text is None and msg.message:
                msg.text = msg.message
            textCheck(msg.text, False, 1, client)

    return channel_id

def main():
    global pos_changed
    pos_changed = True

    config = configparser.ConfigParser()
    config.read('telpbot.ini')
    session_name = config['main']['session_fname']
    api_id = config['main']['api_id']
    api_hash = config['main']['api_hash']
    phone = config['main']['phone_number']

    chatcount = int(config['chat']['count'])
    chatnames = []

    chat_index = 1
    while chat_index <= chatcount:
        chatnames.append(config['chat']['name' + str(chat_index)])
        chat_index = chat_index + 1

    client = TelegramClient(
        session_name,
        api_id=api_id,
        api_hash=api_hash,
        connection_mode=ConnectionMode.TCP_ABRIDGED,
        proxy=None,
        update_workers=1,
        spawn_read_thread=True
    )

    print('Connecting to Telegram servers...')
    if not client.connect():
        print('Initial connection failed. Retrying...')
        if not client.connect():
            print('Could not connect to Telegram servers.')
            return

    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, input('Enter the code ('+phone+'): '))

    print(client.session.server_address)   # Successfull

    #captchaForm(client, 'http://raketa8.ru/ch/0006q.php', '2288w')
    #captchaForm(client, 'http://raketa8.ru/woiijgiowj12oj1o124i214i/', '')
    #captchaForm(client, 'http://raketa8.ru/?page_id=30&preview=true', '')
    #return

    chat_index = 0
    while chat_index < len(chatnames):
        chatnames[chat_index] = checkCurChat(chatnames[chat_index], client)
        time.sleep(1)
        chat_index = chat_index + 1

    print("Channels: " + str(chatnames))

    @client.on(events.NewMessage(chats=chatnames, incoming=True))
    def normal_handler(event):
        textCheck(event.text, True, 0, client)

    print("\n")
    print('Listening for new messages...')

    last_pos = pyautogui.position()
    current_pos_index = 0

    while True:
        time.sleep(0.05)
        current_pos_index = current_pos_index + 1
        if (current_pos_index % 1000 == 0):
            curr_pos = pyautogui.position()
            pos_changed = curr_pos != last_pos
            last_pos = curr_pos
            #if pos_changed:
            #    print("Pos changed")
            #else:
            #    print("Pos NOT changed")

if __name__ == '__main__':
    main()
