import inspect
from langchain_classic.memory.chat_memory import ChatMemory
print(inspect.getsource(ChatMemory._get_input_output))
print('---')
print(inspect.getsource(ChatMemory.save_context))
