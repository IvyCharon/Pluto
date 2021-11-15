import telepot
import time
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup
import random

"""
random: ask 2 inputs -> random, print
toefl: ask next? y -> next -> print; n -> ask number -> print
"""

store = {}
tmp_store={}
class GoldenArches(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(GoldenArches, self).__init__(*args, **kwargs)
        self.indicator = 'begin'
        self.toefl=[]
        with open('TOEFL.txt') as f:
            self.toefl=f.read()
            self.toefl=self.toefl.split('\n\n')


    def on_chat_message(self, msg):
        global store
        global tmp_store
        if msg['text'][0]=='/':
            self.indicator = 'begin'
        if self.indicator == 'begin':
            if msg['text']=='/random':
                bot.sendMessage(msg['from']['id'],'please input the interval using \'2 5\', contains both ends.')
                self.indicator = 'random'
            elif msg['text']=='/toefl':
                bot.sendMessage(msg['from']['id'],'do you want to print the next one?[y/n]', reply_markup=ReplyKeyboardMarkup(keyboard=[['y'],['n']], one_time_keyboard=True))
                self.indicator='whether_next'
            else:
                bot.sendMessage(msg['from']['id'],'sorry I cannot understand what your means.')
                self.indicator='begin'
        elif self.indicator == 'random':
            n=msg['text']
            user=msg['chat']['id']
            n=n.split()
            a=int(n[0])
            b=int(n[1])
            if a < b:
                num=random.randint(a,b)
            else:
                num=random.randint(b,a)
            bot.sendMessage(msg['from']['id'],str(num))
            self.indicator='begin'
        elif self.indicator == 'whether_next':
            user=msg['chat']['id']
            m = msg['text']
            if m=='y':
                if user not in store:
                    store[user]=0
                if store[user] >= 66:
                    bot.sendMessage(msg['from']['id'],'there is no next one.')
                    self.indicator='begin'
                else: 
                    bot.sendMessage(msg['from']['id'],str(store[user]+1)+'. '+self.toefl[store[user]])
                    store[user]=store[user]+1
                    self.indicator = 'begin'
            else:
                bot.sendMessage(msg['from']['id'],'please input the number of the question you want to ask (the maximum is 66).')
                self.indicator='ask_number'
        elif self.indicator == 'ask_number':
            user=msg['chat']['id']
            num = msg['text']
            num=int(num)
            tmp_store[user]=num
            bot.sendMessage(msg['from']['id'],str(num)+'. '+self.toefl[num-1])
            bot.sendMessage(msg['from']['id'],'do you want to change your default number?[y/n]', reply_markup=ReplyKeyboardMarkup(keyboard=[['y'],['n']], one_time_keyboard=True))
            self.indicator='whether_change'
        elif self.indicator == 'whether_change':
            user=msg['chat']['id']
            c=msg['text']
            if c=='y':
                store[user]=tmp_store[user]
                bot.sendMessage(msg['from']['id'],'update success.')
            else:
                bot.sendMessage(msg['from']['id'],'your default number remains the same.')
            self.indicator='begin'
        elif self.indicator == 'help':
            send=''
            bot.sendMessage(msg['from']['id'], send)
            self.indicator='begin'



token=[]
with open('token.txt') as f:
    token=f.read()
    print('token is '+token)

bot = telepot.DelegatorBot(token, [
    pave_event_space()(
        per_chat_id(), create_open, GoldenArches, timeout=30),
])
meMessage=bot.getMe()
if meMessage['is_bot']:
    print('connect success')
else:
    print('cannot connect to telegram')
    quit()
    

MessageLoop(bot).run_as_thread()
print("I'm listening...")

while 1:
    time.sleep(10)