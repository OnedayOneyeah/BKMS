import pinecone
import pickle

# Init pinecone DB for emotion
API_KEY = 'be8c134a-92af-4f8c-ae2c-a2cc127d17f0'
ENVIRONMENT = "gcp-starter"
pinecone.init(api_key = API_KEY, environment = ENVIRONMENT)
print(pinecone.list_indexes())
# pinecone.delete_index("emotion")
pinecone.create_index("emotion", dimension = 768, metric="cosine")
with open('dataset/lyrics_embedding_emotion.pkl', 'rb') as f:
	data = pickle.load(f)

print(f"Length of dataset: {len(data)}")

# Address duplicate data
values = []
count = 0
for i in range(len(data.index)) :
    if data.index[i] in values :
        print("duplicate!:", data.index[i])
        count += 1
    else :
        values.append(data.index[i])
print("duplicate index:", count)

# Insert data into pinecone DB
index = pinecone.Index("emotion")
print(index.describe_index_stats())

for i in range(len(data)) :
    index.upsert([(str(data.index[i]), data['embedding'][data.index[i]].squeeze().tolist())])

print(index.describe_index_stats())

# # Init pinecone DB for textual embeddings
# API_KEY = "12dfbe87-05b3-4243-bb22-e69d329f18ed"
# ENVIRONMENT = "gcp-starter"
# pinecone.init(api_key = API_KEY, environment = ENVIRONMENT)
# pinecone.delete_index("textual")
# pinecone.create_index("textual", dimension = 384, metric="cosine")
# with open('dataset/lyrics_embedding_textual.pkl', 'rb') as f:
# 	data = pickle.load(f)

# print(f"Length of dataset: {len(data)}")

# # Address duplicate data
# values = []
# count = 0
# for i in range(len(data.index)) :
#     if data.index[i] in values :
#         print("duplicate!:", data.index[i])
#         count += 1
#     else :
#         values.append(data.index[i])
# print("duplicate index:", count)

# # # Insert data into pinecone DB
# index = pinecone.Index("textual")
# print(index.describe_index_stats())

# for i in range(len(data)) :
#     index.upsert([(str(data.index[i]), data['embedding'][data.index[i]].squeeze().tolist())])

# print(index.describe_index_stats())

# Init pinecone DB for emotio classes based on music features
# API_KEY = "17adaef6-2910-47b3-bcfb-7735e7d51384"
# ENVIRONMENT = "gcp-starter"
# pinecone.init(api_key = API_KEY, environment = ENVIRONMENT)
# pinecone.delete_index("emotionmusicfeatures")
# pinecone.create_index("emotionmusicfeatures", dimension = 1, metric="cosine")
# with open('dataset/emotion_score.pkl', 'rb') as f:
# 	data = pickle.load(f)

# print(f"Length of dataset: {len(data)}")

# # Address duplicate data
# values = []
# count = 0
# for i in range(len(data.index)) :
#     if data.index[i] in values :
#         print("duplicate!:", data.index[i])
#         count += 1
#     else :
#         values.append(data.index[i])
# print("duplicate index:", count)

# # # Insert data into pinecone DB
# index = pinecone.Index("emotionmusicfeatures")
# print(index.describe_index_stats())

# for i in range(len(data)) :
#     index.upsert([(str(data.index[i]), data.values[i])])

# print(index.describe_index_stats())

