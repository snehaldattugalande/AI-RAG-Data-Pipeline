from app.services.chat import ChatService

service = ChatService()
resp = service.chat('What is the sample facts dataset about?', 'testsession')
print(resp)
