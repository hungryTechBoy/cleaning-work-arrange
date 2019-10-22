# coding=utf-8
import datetime
import email
import imaplib
import smtplib
import time
from email.mime.text import MIMEText

from celery import shared_task

# user = email_addr = 'debo_better@163.com'
# password = "5loveDENGBO"
user = email_addr = 'debo_better@sina.com'
password = "d999e84aa9771497"
on_dutier = ['yuiiwh@163.com', '421309234@qq.com', 'tiffanywa0925@163.com', '779519248@qq.com']
shoveler = {'779519248@qq.com': [4, 5, 6], 'tiffanywa0925@163.com': [2, 3],'yuiiwh@163.com':[0,1]}

# on_dutier = ['tiffanywa0925@163.com']
# shoveler = {'tiffanywa0925@163.com': [2, 3, 6]}

smtp_addr = 'smtp.sina.com'
imap_addr = 'imap.sina.com'


def send_email(to_addr, subject, content):
    msg = MIMEText(content, _charset='utf-8')
    msg['From'] = 'debo <%s>' % email_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    smtp = smtplib.SMTP_SSL(smtp_addr, 465)
    # smtp.set_debuglevel(1)
    # smtp.ehlo("smtp.163.com")
    smtp.login(email_addr, password)
    smtp.sendmail(email_addr, to_addr, msg.as_string())


def finish_work(required_key):
    M = imaplib.IMAP4(host=imap_addr)
    M.debug = 1
    M.login(user, password)
    M.select()
    flag = False

    typ, data = M.search(None, 'UNSEEN')
    for num in reversed(data[0].split()):
        typ, data = M.fetch(num, '(RFC822)')
        text = data[0][1]
        message = email.message_from_string(text)  # 转换为email.message对象

        subject = message.get('subject')

        subject, encoding = email.Header.decode_header(subject)[0]
        from_addr = email.utils.parseaddr(message.get('from'))[1]
        mail_time_stamp = time.mktime(email.utils.parsedate(message['date']))

        cur_time = time.time()
        zero_time = cur_time - (cur_time - time.timezone) % 86400

        if encoding:
            subject = subject.decode(encoding)
        else:
            subject = subject.decode('utf-8')  # 不知道为什么虽然header是汉字但是返回的编码是none

        if mail_time_stamp < zero_time:
            break

        if required_key in subject and from_addr in on_dutier and mail_time_stamp >= zero_time:
            if message.is_multipart():
                playload = message.get_payload()
            else:
                playload = [message]

            for p in playload:
                charset = p.get_content_charset()
                msg = p.get_payload(decode=True)
                msg = msg.decode(charset)

                if u'已经做完' in msg:
                    flag = True
                    break

        M.store(num, '-FLAGS', '(\Seen)')

        if flag:
            break

    M.close()
    M.logout()

    return flag


@shared_task(bind=True)
def send_shovel_shit_task(self):
    week = datetime.datetime.now().weekday()
    for addr, v in shoveler.items():
        if week in v and not finish_work(u'铲屎'):
            subject = "亲,今天轮到你铲屎了哦,加油好好铲!"
            content = """
			注意事项:
			1.如果猫砂看起来比较脏，那可能要换猫砂了
			2.顺便看看需不要加粮和加水

			加油，你是最棒👍的！
			"""

            send_email(addr, subject, content)


@shared_task(bind=True)
def send_on_duty_task(self):
    week_timestamp = 604800
    remain = int(time.time()) / week_timestamp % len(on_dutier)
    if not finish_work(u'值日'):
        subject = "亲,今天轮到你值日了哦,加油好好干！把家里打扫的干干净净的！"
        content = """
					需要清洁的地方:
					1.阳台需要着重清理，四只猫可能会把阳台弄的很脏
					2.洗手间如果比较脏也需要清理下
					3.桌子和沙发猫毛比较多，需要用吸尘器清理
					5.客厅和洗手间的垃圾需要倒掉并换新
					4.其他比较乱的地方也需要整理下

					加油，你是最棒👍的！
					"""

        send_email(on_dutier[remain], subject, content)
