import inspect
from langchain_classic.memory.base import BaseChatMemory
print('file', BaseChatMemory.__module__)
print(inspect.getsource(BaseChatMemory))
