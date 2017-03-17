'''
Created on 2015-4-23

@author: may
'''
import os
import random
users = set()
smallusers = set()
sns = set()
UNUM = 100
user_profile = open('../data/3user_profile.txt')

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "smalldata")
print DATA_DIR

if not os.path.exists(DATA_DIR):
#     print d
    os.mkdir(DATA_DIR)
        
for line in user_profile:
    ids = line.split('\t')
    users.add(int(ids[0]))
for i in range (UNUM):
    smallusers.add(random.randint(0,len(users)-1))
print len(users)
users.clear()
user_profile.close()

user_sns = open('../data/6user_sns.txt')
for line in user_sns:
    ids = line.split('\t')
    u = int(ids[0])
    v = int(ids[1])
    if u in smallusers:
        smallusers.add(v)
        sns.add((u,v))
    if v in smallusers:
        smallusers.add(u)
        sns.add((u,v))

small_user_sns=open('smalldata/small_user_sns.txt','w+')
for e in sns:
    strs = str(e[0])+'\t'+str(e[1])+'\n'
    small_user_sns.write(strs)
    
sns.clear()
small_user_sns.close()
user_sns.close()

user_profile = open('../data/3user_profile.txt')
small_user_profile = open('smalldata/small_user_profile.txt','w+')
for line in user_profile:
    ids = line.split('\t')
    u = int(ids[0])
    if u in smallusers:
#         smallusers.remove(u)
        small_user_profile.write(line)
small_user_profile.close()

user_key_word = open('../data/7user_key_word.txt')
small_user_key_word = open('smalldata/small_key_word.txt','w+')
for line in user_key_word:
    ids = line.split('\t')
    u = int(ids[0])
    if u in smallusers:
#         smallusers.remove(u)
        small_user_key_word.write(line)
small_user_key_word.close()

user_action = open('../data/5user_action.txt')
small_user_action = open('smalldata/small_user_action.txt','w+')
for line in user_action:
    ids = line.split('\t')
    u = int(ids[0])
    v = int(ids[1])
    if (u in smallusers) and (v in smallusers):
#         smallusers.remove(u)
        small_user_action.write(line)
small_user_key_word.close()
print len(smallusers)
smallusers.clear()
    

    
    

