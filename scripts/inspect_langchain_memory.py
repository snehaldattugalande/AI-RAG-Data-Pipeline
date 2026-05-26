import inspect
import langchain_classic.memory as m
print('module', m.__file__)
print('has ConversationBufferMemory', hasattr(m, 'ConversationBufferMemory'))
print('members', [n for n in dir(m) if 'ConversationBufferMemory' in n or 'ChatMemory' in n or 'output' in n.lower()])
print('signature', inspect.signature(m.ConversationBufferMemory.__init__))
print(inspect.getsource(m.ConversationBufferMemory))
