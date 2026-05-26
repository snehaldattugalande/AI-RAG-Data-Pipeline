import langchain_classic.memory as m
print('module file', m.__file__)
for name in dir(m):
    if 'base' in name.lower() or 'chatmemory' in name.lower() or 'memory' in name.lower():
        print(name)
print('members', [name for name in dir(m) if name[0].isupper()])
