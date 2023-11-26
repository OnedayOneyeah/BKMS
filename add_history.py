import psycopg2
from datetime import datetime, date
import pandas as pd
import datetime

from create_table import create_table, delete_table

delete_table()

file_path = 'dataset/diary_examples.csv'
columns = ['timestamp', 'content', 'emotion']
diary = pd.read_csv(file_path, names=columns, header=None, encoding='utf-8')
print(diary)
# 전처리
diary['timestamp'] = pd.to_datetime(diary['timestamp'])
diary['content'] = diary['content'].str.replace("’", "")

diary['year'] = diary['timestamp'].dt.year.astype('int32')
diary['month'] = diary['timestamp'].dt.month.astype('int32')
diary['day'] = diary['timestamp'].dt.day.astype('int32')
diary['hour'] = diary['timestamp'].dt.hour.astype('int32')
diary['minute'] = diary['timestamp'].dt.minute.astype('int32')
print(diary)

# Input 100 contents into DB
connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
conn = psycopg2.connect(connection_info)
try:
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT setval('date_id_seq', (SELECT COALESCE(MAX(id), 1) FROM date), false);
    """)

    # Insert data into the date table
    for i in range(len(diary)):
        year = int(diary.loc[i, 'year'])
        month = int(diary.loc[i, 'month'])
        day = int(diary.loc[i, 'day'])
        hour = int(diary.loc[i, 'hour'])
        minute = int(diary.loc[i, 'minute'])

        cursor.execute("""
            INSERT INTO date(year, month, day, hour, minute) VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (year, month, day, hour, minute))
        date_id = cursor.fetchone()[0]  # Retrieve the generated id

        # Insert data into the diary table
        content = str(diary.loc[i, 'content'])
        cursor.execute("""
            INSERT INTO diary(id, content) VALUES (%s, %s)
        """, (date_id, content))

        emotion = str(diary.loc[i, 'emotion'])
        cursor.execute("""
            INSERT INTO emotion(id, emotion) VALUES (%s, %s)
        """, (date_id, emotion))

    # Commit the changes
    conn.commit()

except psycopg2.Error as e:
    print("DB error: ", e)
    conn.rollback()

finally:
    conn.close()


conn = psycopg2.connect(connection_info)
cursor = conn.cursor()
# Retrieve 5 diary
cursor.execute(f"""
                SELECT emotion FROM emotion LIMIT 3;
                """)
result = cursor.fetchall()
print(result)