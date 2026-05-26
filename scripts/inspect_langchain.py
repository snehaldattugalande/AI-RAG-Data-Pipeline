import langchain_classic.memory.chat_memory as m
print(m.__file__)
print(dir(m))
print('has ChatMemory', hasattr(m, 'ChatMemory'))
print('has ConversationBufferMemory', hasattr(m, 'ConversationBufferMemory'))
try:
    print('ConversationBufferMemory signature:', __import__('inspect').signature(m.ConversationBufferMemory.__init__))
except Exception as e:
    print('sig err', e)
