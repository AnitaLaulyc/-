import json
from pymongo import MongoClient

# 连接到MongoDB
client = MongoClient('mongodb://localhost:27017')
db = client['TestVideos']
collection = db['user_video_list_0909']

# 获取所有数据
all_data = collection.find()

for data in all_data:
    # 获取content字段的值，并将其解析为字典
    content_dict = json.loads(data['content'])

    # 提取所需的字段
    comment_count = content_dict.get('comment_count', '')
    share_count = content_dict.get('share_count', '')

    # 更新MongoDB中的文档，添加新的字段或更新现有字段
    collection.update_one({'_id': data['_id']}, {'$set': {'comment_count': comment_count, 'share_count': share_count}})

# 关闭MongoDB连接
client.close()
