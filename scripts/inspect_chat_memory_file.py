import inspect
import langchain_classic.memory.chat_memory as m
print('module file', m.__file__)
if hasattr(m, 'BaseChatMemory'):
    print('BaseChatMemory signature', inspect.signature(m.BaseChatMemory.__init__))
    print(inspect.getsource(m.BaseChatMemory))
else:
    print('no BaseChatMemory')
print('----')
print('ConversationBufferMemory source start:')
print(inspect.getsource(m.ConversationBufferMemory)[:2000])
