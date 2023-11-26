import psycopg2
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, date
from PIL import Image

import pandas as pd
import openai

from create_table import create_table, delete_table
from classifier import Classifier

# delete_table()
# create_table()

connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"

st.title(f"{date.today().strftime('%Y년 %m월 %d일')}의 일기")
diary_input = st.text_area("여기에 일기를 작성해 주세요 :memo:", height=200)



now = datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
minute = now.minute

if st.button("완성!"):
    # Use chatGPT api to mask private contents in the diary
    mask_setting = """
    could you mask the people's name with [Private Content] from input contents? 
    You should only respond with the masked contents. You should preserve the original input contents except for [Private Content]
    """

    messages = []
    messages.append({'role': "assistant", 'content': mask_setting})
    messages.append({'role': 'user', 'content': diary_input})

    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=messages,
    max_tokens=500,
    )

    masked_diary_input = response['choices'][0]['message']['content']
    # masked_diary_input = diary_input


    # Set chatGPT persona to generate comfort for the input diary
    persona_setting = """Your name is Dr. Jeong. You are an expert in psychotherapy. 
    You hold all the appropriate medical licenses to provide advice. 
    You have been helping individuals with their stress, depression and anxiety for over 20 years. 
    From young adults to older people. Your task is now to give the best advice to individuals 
    seeking help managing their feelings. You must ALWAYS listen to the questioner's emotion, 
    today's experience, past emotion, and past experience BEFORE you answer so that you can 
    better hone in on what the questioner is really trying to talk about and feel. 
    Past emotions and past experiences will be given as a list form, 
    the emotion and experience at the same index is matching. There might be no past emotions and experiences.
    You must treat me as a person who needs warm comments. 
    Your response format should focus on the questioner's emotions and experiences. 
    Your response format also should focus on the questioner's present emotions and experiences 
    more than the past ones. The song title will be given also as background music of the 
    questioner's experiences. DO NOT INCLUDE THE WORD '[PRIVATE CONTENT]' in your response."""

    messages_comfort = []
    messages_comfort.append({'role': "assistant", 'content': persona_setting})

    # Make input
    current_experience = masked_diary_input
    # Emotion classifier
    classifier = Classifier()
    current_emotion, _ = classifier(current_experience)
    # load previous diary and emotion
    conn = psycopg2.connect(connection_info)
    cursor = conn.cursor()
    # Retrieve 5 diary
    cursor.execute(f"""
                    SELECT content FROM diary LIMIT 5;
                    """)
    result = cursor.fetchall()
    previous_experiences = list(map(lambda x: x[0], result)) if len(result) > 0 else []

    cursor.execute(f"""
                    SELECT emotion FROM emotion LIMIT 5;
                    """)
    result = cursor.fetchall()
    previous_emotions = list(map(lambda x: x[0], result)) if len(result) > 0 else []


    scores, selected_ids = classifier.compute_scores()
    topk_music_ids = classifier.return_topk_music(scores, selected_ids, top_k=2).squeeze().tolist()
    song_db = pd.read_csv('dataset/spotify_data.csv')
    columns = list(song_db.columns)
    columns[0] = 'song_idx'
    song_db.columns = columns
    selected_rows = song_db[song_db['song_idx'].isin(topk_music_ids)]
    song_titles = list(selected_rows['track_name'])
    song_title = song_titles[0]

    song_lyrics = list(selected_rows['lyrics'])[0]

    

    user_message = f"""
                        1. Emotion type: {current_emotion} 
                        2. Experience: {current_experience} 
                        3. Song title: {song_title} 
                        4. Song lyrics {song_lyrics}
                        5: Previous emotion types: {previous_emotions} 
                        6: Previous experiences: {previous_experiences}
                    """
    user_message = user_message.strip()
    messages_comfort.append({'role': 'user', 'content': user_message})

    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=messages_comfort,
    max_tokens=500,
    )

    comment = response['choices'][0]['message']['content']

    # Modify ' to avoid sql error
    current_experience = current_experience.replace("'", "''")
    song_title = song_title.replace("'", "''")
    song_lyrics = song_lyrics.replace("'", "''")
    comment = comment.replace("'", "''")
    # For test, will be removed
    st.write(f"작성한 일기: {diary_input}")
    st.write(f"마스킹된 일기: {masked_diary_input}")
    st.write(f"당신의 추정 감정: {current_emotion}")
    st.write(f"추천된 노래: {song_title}")
    st.write(f"추천된 노래 가사: {song_lyrics}")
    st.write(f"과거 감정: {previous_emotions}")
    st.write(f"과거 일기: {previous_experiences}")
    st.write(f"한마디: {comment}")

    conn = psycopg2.connect(connection_info)
    cursor = conn.cursor()

    try:
      # date 테이블에서 현재 날짜에 해당하는 id 조회
      cursor.execute(f"""
            SELECT id FROM date WHERE year = {year} AND month = {month} AND day = {day};
        """)
      result = cursor.fetchone()

      if result is not None:
        id = result[0]
        cursor.execute(f'''
                UPDATE diary SET content = '{diary_input}' WHERE id = {id};
            ''')
        cursor.execute(f'''
                UPDATE diary_masked SET content = '{masked_diary_input}' WHERE id = {id};
            ''')
        cursor.execute(f'''
                UPDATE emotion SET emotion = '{current_emotion}' WHERE id = {id};
            ''')
        cursor.execute(f'''
                UPDATE recommend SET music = '{song_title}' WHERE id = {id};
            ''')
        cursor.execute(f'''
                UPDATE comment SET content = '{comment}' WHERE id = {id};
            ''')
      else:
        # 현재 날짜에 해당하는 diary가 존재하지 않는 경우, date 테이블과 diary 테이블에 새로운 diary 추가
        cursor.execute(f'''
            INSERT INTO date(year, month, day, hour, minute) VALUES ({year}, {month}, {day}, {hour}, {minute}) RETURNING id;
        ''')
        id = cursor.fetchone()[0]
        cursor.execute(f'''
            INSERT INTO diary(id, content) VALUES ({id}, '{diary_input}');
        ''')
        cursor.execute(f'''
            INSERT INTO diary_masked(id, content) VALUES ({id}, '{masked_diary_input}');
        ''')
        cursor.execute(f'''
            INSERT INTO emotion(id, emotion) VALUES ({id}, '{current_emotion}');
        ''')
        cursor.execute(f'''
            INSERT INTO recommend(id, music) VALUES ({id}, '{song_title}');
        ''')
        cursor.execute(f'''
            INSERT INTO comment(id, content) VALUES ({id}, '{comment}');
        ''')
        

        
      conn.commit()
      st.success("일기가 성공적으로 작성되었습니다! :100:")
      


    except Exception as e:
      st.error("일기 작성에 실패했습니다")
      st.error(e)
      print(e)

    finally:
      conn.close()

with st.sidebar:
    options = ["오늘의 기록", "과거의 기록"]
    choice = option_menu("Menu", options,
                         icons=['bi bi-calendar-heart', 'bi bi-calendar-heart-fill'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "4!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
        "nav-link-selected": {"background-color": "#08c7b4"},
    }
    )

col1, col2 = st.columns([2,3])
col3, col4 = st.columns([2,3])

# 오늘 작성한 일기를 보고 싶다!
if choice == "오늘의 기록":

    with col1:
        st.header("Playlist 🎧")
        st.image('https://img.freepik.com/vetores-premium/design-de-vetor-simples-do-music-player-com-faixa-de-botoes-e-interface-de-player-de-audio-de-titulo_505988-666.jpg')

    with col2: # 여기에 추천노래 들어갈 것!
        st.header("")

    st.header("Cheer up")
    st.header("Today's record")
    try:
        conn = psycopg2.connect(connection_info)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT id FROM date WHERE year = {year} AND month = {month} AND day = {day};
        """)
        result = cursor.fetchone()
        if result is not None:
            id = result[0]
            cursor.execute(f"""
                SELECT content FROM diary WHERE id = {id};
            """)
            diary = cursor.fetchone()
            if diary is not None:
                st.write(diary[0])
            else:
                st.write("오늘의 기록이 없습니다.")
        else:
            st.write("오늘의 기록이 없습니다.")
    except Exception as e:
        st.error("일기 검색에 실패했습니다.")
        st.error(e)
    finally:
        conn.close()

# 과거에 작성한 일기를 보고 싶다!
elif choice == "과거의 기록":

    with col3:
        st.header("Playlist 🎧")
        st.image('https://img.freepik.com/vetores-premium/design-de-vetor-simples-do-music-player-com-faixa-de-botoes-e-interface-de-player-de-audio-de-titulo_505988-666.jpg')

    with col4: # 여기에 추천노래 들어갈 것!
        st.header("")

    st.header("Cheer up 🫂")
    st.header("Past diary")
    selected_date = st.date_input("날짜를 선택하세요.", date.today())
    selected_year = selected_date.year
    selected_month = selected_date.month
    selected_day = selected_date.day
    try:
        conn = psycopg2.connect(connection_info)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT id FROM date WHERE year = {selected_year} AND month = {selected_month} AND day = {selected_day};
        """)
        result = cursor.fetchone()
        if result is not None:
            id = result[0]
            cursor.execute(f"""
                SELECT content FROM diary WHERE id = {id};
            """)
            diary = cursor.fetchone()
            if diary is not None:
                st.write(diary[0])
            else:
                st.write(f"{selected_date}의 기록이 없습니다.")
        else:
            st.write(f"{selected_date}의 기록이 없습니다.")
    except Exception as e:
        st.error("일기 검색에 실패했습니다.")
        st.error(e)
    finally:
        conn.close()


