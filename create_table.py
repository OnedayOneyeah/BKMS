# CREATE TABLE
import psycopg2

def alter_table():
    
    connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
    conn = psycopg2.connect(connection_info)
    print(connection_info)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            ALTER TABLE recommend 
            ADD music4 text, 
            ADD artist4 text, 
            ADD music5 text ,
            ADD artist5 text ,
            ADD music6 text, 
            ADD artist6 text, 
            ADD music7 text, 
            ADD artist7 text, 
            ADD music8 text, 
            ADD artist8 text, 
            ADD music9 text, 
            ADD artist9 text, 
            ADD music10 text, 
            ADD artist10 text, 
            ADD music11 text, 
            ADD artist11 text, 
            ADD music12 text, 
            ADD artist12 text;
                       """)
        conn.commit()
    except psycopg2.Error as e:
        print("DB error: ", e)
        conn.rollback()
    
    finally:
        conn.close()

def create_table():
    connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
    conn = psycopg2.connect(connection_info)

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS date(id SERIAL PRIMARY KEY, year int, month int, day int, hour int, minute int);
            CREATE TABLE IF NOT EXISTS diary(id SERIAL PRIMARY KEY, content text);
            CREATE TABLE IF NOT EXISTS diary_masked(id SERIAL PRIMARY KEY, content text);
            CREATE TABLE IF NOT EXISTS emotion(id SERIAL PRIMARY KEY, emotion text, score int);
            CREATE TABLE IF NOT EXISTS recommend(id SERIAL PRIMARY KEY, music1 text, artist1 text, music2 text, artist2 text, music3 text, artist3 text);
            CREATE TABLE IF NOT EXISTS comment(id SERIAL PRIMARY KEY, content text);
            ALTER TABLE diary ADD FOREIGN KEY(id) REFERENCES date(id);
            ALTER TABLE diary_masked ADD FOREIGN KEY(id) REFERENCES date(id);
            ALTER TABLE emotion ADD FOREIGN KEY(id) REFERENCES date(id);
            ALTER TABLE recommend ADD FOREIGN KEY(id) REFERENCES date(id);
            ALTER TABLE comment ADD FOREIGN KEY(id) REFERENCES date(id);
        """)
        conn.commit()

    except psycopg2.Error as e:
        print("DB error: ", e)
        conn.rollback()

    finally:
        conn.close()

def delete_table():
    connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
    conn = psycopg2.connect(connection_info)

    try:
        cursor = conn.cursor()
        cursor.execute("""
            DROP TABLE IF EXISTS date CASCADE;
            DROP TABLE IF EXISTS diary CASCADE;
            DROP TABLE IF EXISTS diary_masked CASCADE;
            DROP TABLE IF EXISTS emotion CASCADE;
            DROP TABLE IF EXISTS recommend CASCADE;
            DROP TABLE IF EXISTS comment CASCADE;
        """)
        conn.commit()

    except psycopg2.Error as e:
        print("DB error: ", e)
        conn.rollback()

    finally:
        conn.close()