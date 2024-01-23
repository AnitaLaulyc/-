# coding: utf-8
import pandas as pd
import jieba
import time
import pymongo

# -------------------------------------获取数据集---------------------------------
client=pymongo.MongoClient("mongodb://localhost:27017")
db=client["TestVideos"]
collection=db["user_video_list_0909"]

# -------------------------------------情感词典读取-------------------------------
# 注意：
# 1.词典中怒的标记(NA)识别不出被当作空值,情感分类列中的NA都给替换成NAU
# 2.大连理工词典中有情感分类的辅助标注(有NA),故把情感分类列改好再替换原词典中

# 扩展前的词典
df = pd.read_excel(r"C:\Users\Lenovo\Desktop\情绪分类及特征提取（大连理工词典）\大连理工大学中文情感词汇本体NAU.xlsx")
print(df.head(10))

df = df[['词语', '词性种类', '词义数', '词义序号', '情感分类', '强度', '极性']]
df.head()

# -------------------------------------七种情绪的运用-------------------------------
Happy = []
Good = []
Surprise = []
Anger = []
Sad = []
Fear = []
Disgust = []

# df.iterrows()功能是迭代遍历每一行
for idx, row in df.iterrows():
    if row['情感分类'] in ['PA', 'PE']:
        Happy.append(row['词语'])
    if row['情感分类'] in ['PD', 'PH', 'PG', 'PB', 'PK']:
        Good.append(row['词语'])
    if row['情感分类'] in ['PC']:
        Surprise.append(row['词语'])
    if row['情感分类'] in ['NB', 'NJ', 'NH', 'PF']:
        Sad.append(row['词语'])
    if row['情感分类'] in ['NI', 'NC', 'NG']:
        Fear.append(row['词语'])
    if row['情感分类'] in ['NE', 'ND', 'NN', 'NK', 'NL']:
        Disgust.append(row['词语'])
    if row['情感分类'] in ['NAU']:  # 修改: 原NA算出来没结果
        Anger.append(row['词语'])

    # 正负计算不是很准 自己可以制定规则
Positive = Happy + Good + Surprise
Negative = Anger + Sad + Fear + Disgust
print('情绪词语列表整理完成')
print(Anger)

# ---------------------------------------中文分词---------------------------------

# 添加自定义词典和停用词
# jieba.load_userdict("user_dict.txt")
# 加载停用词
with open(r"C:\Users\Lenovo\Desktop\情绪分类及特征提取（大连理工词典）\stop_words.txt", 'r', encoding='utf-8') as stop_words_file:
    stop_list = [line.strip() for line in stop_words_file]

stop_list = set(stop_list)

def txt_cut(juzi):
    return [w for w in jieba.lcut(juzi) if w not in stop_list]  # 可增加len(w)>1


# ---------------------------------------情感计算---------------------------------
def emotion_caculate(text):
    positive = 0
    negative = 0

    anger = 0
    disgust = 0
    fear = 0
    sad = 0
    surprise = 0
    good = 0
    happy = 0

    anger_list = []
    disgust_list = []
    fear_list = []
    sad_list = []
    surprise_list = []
    good_list = []
    happy_list = []

    wordlist = txt_cut(text)
    # wordlist = jieba.lcut(text)
    wordset = set(wordlist)
    wordfreq = []
    for word in wordset:
        freq = wordlist.count(word)
        if word in Positive:
            positive += freq
        if word in Negative:
            negative += freq
        if word in Anger:
            anger += freq
            anger_list.append(word)
        if word in Disgust:
            disgust += freq
            disgust_list.append(word)
        if word in Fear:
            fear += freq
            fear_list.append(word)
        if word in Sad:
            sad += freq
            sad_list.append(word)
        if word in Surprise:
            surprise += freq
            surprise_list.append(word)
        if word in Good:
            good += freq
            good_list.append(word)
        if word in Happy:
            happy += freq
            happy_list.append(word)

    emotion_info = {
        'length': len(wordlist),
        'positive': positive,
        'negative': negative,
        'anger': anger,
        'disgust': disgust,
        'fear': fear,
        'good': good,
        'sadness': sad,
        'surprise': surprise,
        'happy': happy,

    }

    indexs = ['length', 'positive', 'negative', 'anger', 'disgust', 'fear', 'sadness', 'surprise', 'good', 'happy']
    # return pd.Series(emotion_info, index=indexs), anger_list, disgust_list, fear_list, sad_list, surprise_list, good_list, happy_list
    return pd.Series(emotion_info, index=indexs)


# ---------------------------------------情感计算---------------------------------

start = time.time()
for news_document in collection.find():
    news_text = news_document.get("content", "")  # 假设新闻文本字段名为 "content"
    emotion_info = emotion_caculate(news_text)

    # 更新 MongoDB 中的情感值字段，假设情感值字段名为 "emotion_score"
    update_query = {"_id": news_document["_id"]}
    update_values = {"$set": {"emotion_score": emotion_info.to_dict()}}
    collection.update_one(update_query, update_values)

end_time = time.time()
print(f"情感分析完成，总共耗时: {end_time - start} 秒。")