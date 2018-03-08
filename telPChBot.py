import sys
import time
import re
import random
import webbrowser
import configparser

from pyquery import PyQuery as pq

from telethon import utils, events, TelegramClient, ConnectionMode
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.extensions import markdown

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException   


def isCryptoBotUrl(url):
    url_res_t0 = re.findall("(?P<url>https?://telegram.me/[^\s()]+_CHANGE_BOT[^\s()]+)", url)
    if url_res_t0:
        return True
    return False

def captchaForm(client, url):
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        mainWin = driver.current_window_handle  
        driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[0])
        CheckBox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID ,"recaptcha-anchor"))
        )
        time.sleep(0.3)
        CheckBox.click()
        driver.switch_to_window(mainWin)
        time.sleep(0.2)
        cur_url = driver.current_url
        driver.find_elements_by_tag_name("iframe")[0].submit()
        WebDriverWait(driver, 10).until(EC.url_changes(cur_url))

        if driver.current_url != cur_url:
            if not isCryptoBotUrl(driver.current_url):
                time.sleep(0.5)
                if isCryptoBotUrl(driver.current_url):
                    print("Found: " + driver.current_url)
                    botStart(client, driver.current_url)
                else:
                    print("NOT Found: " + driver.current_url)
            else:
                print("Found: " + driver.current_url)
                botStart(client, driver.current_url)
        else:
            print("NOT Found: " + driver.current_url)

    finally:
        driver.close()
        driver.service.stop()


def botStart(client, url):
    p = re.compile('https?://telegram.me/(BTC_CHANGE_BOT|ETH_CHANGE_BOT)\?start=([0-9a-zA-Z]+)')
    m = p.match(url)
    if m.group(2):
        client.send_message(m.group(1), '/start ' + m.group(2))

def linkCheck(url, doopen, client, deep):
    print("Checking " + url)
    d = pq(url=url)

    p = d('a[href^="https://telegram.me/BTC_CHANGE_BOT"]:first,a[href^="https://telegram.me/ETH_CHANGE_BOT"]:first')
    if p.length > 0:
        aim = p.attr('href')
        print("Found: " + aim)
        if (doopen):
            botStart(client, aim)

    p = d('form .g-recaptcha')
    if p.length > 0:
        print("Found: " + url)
        if (doopen):
            captchaForm(client, url)
            #webbrowser.open(url, 1, True)

    if deep < 5:
        p = d('a[href^="http://raketa8.ru/c"]:first')
        if p.length > 0:
            aim = p.attr('href')
            linkCheck(url, doopen, client, deep+1)


def textCheck(txt, doopen, delay_s, client):
    print("______________________________________")
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    txt = txt.translate(non_bmp_map)
    print(txt)
    print("______________________________________")

    url_res_t0 = re.findall("(?P<url>https?://telegram.me/[^\s()]+_CHANGE_BOT[^\s()]+)", txt)
    if url_res_t0:
        random.shuffle(url_res_t0)
        for url in url_res_t0:
            print("Found: " + url)
            if (doopen):
                botStart(client, url)
            time.sleep(delay_s)

    url_res_t1 = re.findall("(?P<url>http?://telegra.ph/[^\s()]+)", txt)
    if url_res_t1:
        random.shuffle(url_res_t1)
        for url in url_res_t1:
            linkCheck(url, doopen, client, 0)
            time.sleep(delay_s)

    url_res_t2 = re.findall("(?P<url>http?://raketa8.ru/c[^\s()]+)", txt)
    if url_res_t2:
        random.shuffle(url_res_t2)
        for url in url_res_t2:
            linkCheck(url, doopen, client, 0)
            time.sleep(delay_s)

def checkCurChat(chatname, client):
    response = client.invoke(ResolveUsernameRequest(chatname))
    for msg in client.get_message_history(response.peer, limit=1):
        if not hasattr(msg, 'text'):
            msg.text = None
        if msg.text is None:
            if not msg.entities:
                msg.text = msg.message
            msg.text = markdown.unparse(msg.message,
                                        msg.entities or [])
        textCheck(msg.text, False, 2, client)

def main():
    config = configparser.ConfigParser()
    config.read('telpbot.ini')
    session_name = config['main']['session_fname']
    api_id = config['main']['api_id']
    api_hash = config['main']['api_hash']
    phone = config['main']['phone_number']
    chatname1 = config['chat']['name1']
    chatname2 = config['chat']['name2']

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

    checkCurChat(chatname1, client)
    time.sleep(1)
    checkCurChat(chatname2, client)
    time.sleep(1)

    @client.on(events.NewMessage(chats=[chatname1,chatname2], incoming=True))
    def normal_handler(event):
        textCheck(event.text, True, 0, client)

    print('Listening for new messages...')

    while True:
        time.sleep(0.1)

if __name__ == '__main__':
    main()
