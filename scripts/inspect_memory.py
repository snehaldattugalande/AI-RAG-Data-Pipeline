import inspect
from langchain_classic.memory import ConversationBufferMemory
print(inspect.signature(ConversationBufferMemory.__init__))
print([a for a in dir(ConversationBufferMemory) if 'output' in a.lower()])
print([a for a in dir(ConversationBufferMemory) if 'key' in a.lower()])
