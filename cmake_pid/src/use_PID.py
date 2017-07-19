from PID import PID

# create drow instance
m_pid = PID(10, 1, 2)

# access the word and print it
print m_pid.windup_limit

print m_pid.get_PID()
# # print the chars
# for char in d.get_chars():
#     print char

# # check out if it works for a list
# # it will join the words and save them in word variable
# d = drow(['cat', 'dog', 'canary'])

# # print me joined
# print d.word
