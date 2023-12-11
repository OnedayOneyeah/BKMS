# SQL initial setting
import psycopg2
connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
conn = psycopg2.connect(connection_info)
try:
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.year, d.month, d.day, e.emotion 
        FROM (date d
            NATURAL JOIN emotion e);
    """)
    dates_and_emotions = cursor.fetchall()

    # Commit the changes
    conn.commit()

except psycopg2.Error as e:
    print("DB error: ", e)
    conn.rollback()

finally:
    conn.close()

import pandas as pd
import datetime
# preprocessing
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
    # print(emo)
    return label2id[emo]

dates_by_date = [datetime.date(date[0],date[1], date[2]) for date in dates_and_emotions]
# emotion_by_date = list(map(emo2idx, [emo[3] for emo in dates_and_emotions]))
emotion_by_date = [emo[3] for emo in dates_and_emotions]

df = pd.DataFrame({'Date':dates_by_date, 'Emotion': emotion_by_date, 'y': [1]*len(dates_by_date)})
limit = 30
df = df[-limit:]

# visualization
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

palette ={"anger": "red", "disgust": "yellow", "fear": "blue", "joy": "pink", "neutral":"green", "sadness":"darkblue", "surprise":"purple"}

fig, ax = plt.subplots(figsize=(10, 3), dpi=80, facecolor='w', edgecolor='w', frameon=True)
# fig.patch.set_alpha(0.7)  # Adjust alpha for the entire figure

ax = sns.scatterplot(
    x = 'Date',
    y = 'y',
    hue = 'Emotion',
    data = df,
    s = 200,
    alpha = 0.5,
    palette=palette
)

ax.set_yticks([])
ax.set_ylabel('')
ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha='right')
ax.set(title = 'Diary History')
ax.spines['top'].set_alpha(0.3)
ax.spines['right'].set_alpha(0.3)
ax.spines['bottom'].set_alpha(0.3)
ax.spines['left'].set_alpha(0.3)

legend = ax.legend()
legend.get_frame().set_facecolor('#f0f0f0')  # Replace 'your_legend_color_here' with the desired color

plt.show()