import psycopg2
from datetime import datetime, date
import pandas as pd
import datetime

if __name__ == '__main__':
    connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
    conn = psycopg2.connect(connection_info)
    try:
        print("저 실행됐어요")
        cursor = conn.cursor()

        year = 2023
        month =11
        day = 1
        hour = 13
        minute = 50
        cursor.execute(f"""
                        SELECT id FROM date WHERE year = {year} AND month = {month} AND day = {day};
                    """)
        result = cursor.fetchone()
        id = result[0]

        music1 = 'Sunday Morning'
        artist1 = 'Maroon 5'
        music2 = 'Basket Case'
        artist2 = 'Green Day'
        music3 = 'sheluvme'
        artist3 = 'Tai Verdes'

        if result is not None:
            cursor.execute("""
                INSERT INTO recommend(id, music1, music2, music3, artist1, artist2, artist3) VALUES (%s, %s, %s, %s, %s, %s, %s) 
            """, (id, music1, music2, music3, artist1, artist2, artist3 ))

        year = 2023
        month = 10
        day = 31
        hour = 13
        minute = 50
        cursor.execute(f"""
                        SELECT id FROM date WHERE year = {year} AND month = {month} AND day = {day};
                    """)
        result = cursor.fetchone()
        id = result[0]

        music1 = 'Make It To Christmas'
        artist1 = 'Alessia Cara'
        music2 = 'I Like Me Better'
        artist2 = 'Lauv'
        music3 = 'West Coast Love'
        artist3 = 'Emotional Oranges'

        if result is not None:
            cursor.execute("""
                INSERT INTO recommend(id, music1, music2, music3, artist1, artist2, artist3) VALUES (%s, %s, %s, %s, %s, %s, %s) 
            """, (id, music1, music2, music3, artist1, artist2, artist3 ))
        conn.commit()
    except psycopg2.Error as e:
        print("DB error: ", e)
        conn.rollback()
    finally:
        conn.close()
    

