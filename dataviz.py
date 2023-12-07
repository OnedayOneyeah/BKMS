# SQL initial setting
import psycopg2
connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
conn = psycopg2.connect(connection_info)
try:
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM date;
    """)
    dates = cursor.fetchall()
    cursor.execute("""
                SELECT * FROM emotion;
                   """)
    emotions = cursor.fetchall()

    # Commit the changes
    conn.commit()

except psycopg2.Error as e:
    print("DB error: ", e)
    conn.rollback()

finally:
    conn.close()

# preprocessing
limit = 30
import datetime
dates_by_date = [datetime.date(date[1],date[2], date[3]) for date in dates][-limit:]

def emo2idx(emo:str):
    label2id = {
    "anger": 0,
    "disgust": 1,
    "fear": 2,
    "joy": 3,
    "neutral": 4,
    "sadness": 5,
    "surprise": 6
  }
    print(emo)
    return label2id[emo]
    
emotion_by_date = [emo[1] for emo in emotions][-limit:]
emotion_by_date = list(map(emo2idx, emotion_by_date))

# visualization
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

colors = ListedColormap(['red','yellow','blue','pink', 'green', 'darkblue', 'purple'])
legend_labels = list(['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']) 

plt.figure(figsize=(35,5))

scatter = plt.scatter(dates_by_date, # x축
            [1]*len(dates_by_date), # y축
            s = 1000, # 사이즈
            c = emotion_by_date, # 색깔(고정)
            alpha = 0.5,
            cmap = colors
          ) # 투명도

plt.xlabel('Date', size = 30)
plt.ylabel('', size = 12)
plt.yticks([])
plt.xticks(size = 20)
plt.title('Diary History', size = 30)
plt.legend(handles = scatter.legend_elements()[0], labels = legend_labels, fontsize = 20)
plt.show()