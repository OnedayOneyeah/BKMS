# CREATE TABLE
import psycopg2

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
            CREATE TABLE IF NOT EXISTS recommend(id SERIAL PRIMARY KEY, music text);
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
            TRUNCATE TABLE date CASCADE;
            TRUNCATE TABLE diary CASCADE;
            TRUNCATE TABLE diary_masked CASCADE;
            TRUNCATE TABLE emotion CASCADE;
            TRUNCATE TABLE recommend CASCADE;
            TRUNCATE TABLE comment CASCADE;
        """)
        conn.commit()

    except psycopg2.Error as e:
        print("DB error: ", e)
        conn.rollback()

    finally:
        conn.close()