import sys
import time
import re
import webbrowser
import configparser
from pyquery import PyQuery as pq
from telethon import utils, events, TelegramClient, ConnectionMode
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.extensions import markdown

def textCheck(txt, doopen, delay_s):
    print("______________________________________")
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    txt = txt.translate(non_bmp_map)
    print(txt)
    print("______________________________________")

    url_res_t0 = re.findall("(?P<url>https?://telegram.me/[^\s()]+_CHANGE_BOT[^\s()]+)", txt)
    if url_res_t0:
        for url in url_res_t0:
            print("Found: " + url)
            if (doopen):
                webbrowser.open(url, 1, True)
            time.sleep(delay_s)

    url_res_t1 = re.findall("(?P<url>http?://telegra.ph/[^\s()]+)", txt)
    if url_res_t1:
        for url in url_res_t1:
            print("Checking " + url)
            d = pq(url=url)
            p = d('a[href^="https://telegram.me/"]:first')
            if p.length > 0:
                aim = p.attr('href')
                print("Found: " + aim)
                if (doopen):
                    webbrowser.open(aim, 1, True)
            else:
                p = d('a[href^="http://raketa8.ru/c"]:first')
                if p.length > 0:
                    aim = p.attr('href')
                    print("Found: " + aim)
                    if (doopen):
                        webbrowser.open(aim, 1, True)
            time.sleep(delay_s)

    url_res_t2 = re.findall("(?P<url>http?://raketa8.ru/c[^\s()]+)", txt)
    if url_res_t2:
        for url in url_res_t2:
            print("Checking " + url)
            d = pq(url=url)
            p = d('a[href^="https://telegram.me/"]:first')
            if p.length > 0:
                aim = p.attr('href')
                print("Found: " + aim)
                if (doopen):
                    webbrowser.open(aim, 1, True)
            else:
                p = d('form .g-recaptcha')
                if p.length > 0:
                    print("Found: " + url)
                    if (doopen):
                        webbrowser.open(url, 1, True)
            time.sleep(delay_s)

def checkCurChat(chatname, client):
    response = client.invoke(ResolveUsernameRequest(chatname))
    for msg in client.get_message_history(response.peer, limit=2):
        if not hasattr(msg, 'text'):
            msg.text = None
        if msg.text is None:
            if not msg.entities:
                msg.text = msg.message
            msg.text = markdown.unparse(msg.message,
                                        msg.entities or [])
        textCheck(msg.text, False, 2)

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
        textCheck(event.text, True, 0)

    print('Listening for new messages...')

    while True:
        time.sleep(0.5)

if __name__ == '__main__':
    main()
