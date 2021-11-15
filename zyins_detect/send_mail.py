from os import name
import getTimes
import smtplib
from email.mime.text import MIMEText
import sys
import time

with open('sender.txt') as f:
    sender=f.read()
with open('query.txt') as f:
    query=f.read()
    query=query.split()
with open('mails.txt') as f:
    mails=f.read()
    mails=mails.split()
with open('names.txt') as f:
    names=f.read()
    names=names.split()
with open('token.txt') as f:
    token=f.read()
with open('host.txt') as f:
    h=f.read()
    host=[]
    host.append(h)
with open('host_name.txt') as f:
    host_name=f.read()

print('begin working ...')
print('sender: ', sender)
print('query: ', query)
print('mails: ', mails)
print('names: ', names)
print('host: ', host)
print('host_name: ', host_name)

n = len(query)
number = []

def sth_wrong(content, host_name, sender, receiver, token):
    title = '沙龙统计次数程序出锅啦！'
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receiver)
    message['Subject'] = title
    smtp = smtplib.SMTP_SSL('smtp.126.com', 465)
    smtp.login(host_name, token) 
    smtp.sendmail(sender, receiver, message.as_string()) 
    smtp.quit()

if len(mails) != n or len(names) != n:
    sth_wrong('输入不对呀qvq', host_name, sender, host, token)
    sys.exit()
    
for i in range(0, n):
    ans = getTimes.getTimes(query[i])
    number.append(ans)
    receiver = [mails[i]]
    content = '您的致远沙龙次数开始查询，每当次数增加，我都会为您发送一封邮件。有问题请联系@ivy，欢迎提出意见与建议！'
    title = 'ivybot竭诚为您服务'
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receiver)
    message['Subject'] = title
    try:
        smtp = smtplib.SMTP_SSL('smtp.126.com', 465)
        smtp.login(host_name, token) 
        smtp.sendmail(sender, receiver, message.as_string()) 
        smtp.quit()
    except smtplib.SMTPException as e:
        sth_wrong('a mail was not sent successfully!', host_name, sender, host, token)
        print(query[i])
        print(mails[i])
        print(names[i])
        print(str(number[i]))
        sys.exit()


while(True):
    print(time.asctime(time.localtime(time.time())))
    print("Checking for zy-ins...")
    for i in range(n):
        ans = getTimes.getTimes(query[i])
        print('[check] '+names[i]+'\'s zy-ins times is',ans)
        if ans == -1:
            sth_wrong(names[i]+'的学号不对哦~', host_name, sender, host, token)
            sys.exit()
        if ans == number[i]:
            continue
        
        print('[change] '+names[i] + '\'s zy-ins time changed from {} to {}'.format(number[i], ans))
        receiver = [mails[i]]
        content = '\t你的 zy-ins 沙龙次数增加了！从'+str(number[i])+'变成了'+str(ans)+'！'
        if ans == 16:
            content = content+'\n\t恭喜你，zy-ins 沙龙次数达标！可以毕业啦！'
        number[i] = ans
        title = 'zy-ins 沙龙次数统计'
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(receiver)
        message['Subject'] = title
        try:
            smtp = smtplib.SMTP_SSL('smtp.126.com', 465)
            smtp.login(host_name, token)
            smtp.sendmail(sender, receiver, message.as_string()) 
            smtp.quit()
        except smtplib.SMTPException as e:
            sth_wrong('a mail was not sent successfully!', host_name, sender, host, token)
            print(query[i])
            print(mails[i])
            print(names[i])
            print(str(number[i]))
            sys.exit()
        print('[mail] mail to '+names[i]+' was sent successfully!')
    time.sleep(3600)
