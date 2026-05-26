from app.services.storage import VectorStore

v = VectorStore()
print('embed client type:', type(v.embedding_client))
print('embed class module:', v.embedding_client.__class__.__module__)
print('embed client repr:', repr(v.embedding_client))
