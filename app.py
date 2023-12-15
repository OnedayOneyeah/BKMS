import psycopg2
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, date
from PIL import Image
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

import pandas as pd
import openai

from create_table import create_table, delete_table, alter_table
from classifier import Classifier

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

alter_table()

connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"

st.title(f"{date.today().strftime('%Y년 %m월 %d일')}의 일기")
diary_input = st.text_area("여기에 일기를 작성해 주세요 :memo:", height=150)

now = datetime.now()
year = now.year
month = now.month
day = now.day
hour = now.hour
minute = now.minute

song_titles_out = []
song_artists_out = []
song_lyrics_out = []

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

    # masked_diary_input = response['choices'][0]['message']['content']
    masked_diary_input = diary_input

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
    questioner's experiences. DO NOT INCLUDE THE WORD '[PRIVATE CONTENT]' in your response.
    do not respond more than 5 lines."""

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
    topk_music_ids = classifier.return_topk_music(scores, selected_ids, top_k=12).squeeze().tolist()
    # print(len(scores), len(selected_ids), len(topk_music_ids))
    song_db = pd.read_csv('dataset/spotify_data_extended.csv')
    columns = list(song_db.columns)
    columns[0] = 'song_idx'
    song_db.columns = columns
    selected_rows = song_db[song_db['song_idx'].isin(topk_music_ids)]
    # print(selected_rows, len(selected_rows))
    song_artists = list(selected_rows['track_artist'])
    song_titles = list(selected_rows['track_name']) # 추천 음악의 제목
    song_lyrics = list(selected_rows['lyrics'])

    song_titles_out.extend(song_titles)
    song_artists_out.extend(song_artists)

    song_titles_input = song_titles[0]
    song_lyrics_input = song_lyrics[0]

    user_message = f"""
                        1. Emotion type: {current_emotion} 
                        2. Experience: {current_experience} 
                        3. Song title: {song_titles_input} 
                        4. Song lyrics {song_lyrics_input}
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
    try:
        comment = response['choices'][0]['message']['content']
    except:
        comment = 'wow!'

    # Modify ' to avoid sql error
    current_experience = current_experience.replace("'", "''")
    song_titles = list(map(lambda x: x.replace("'", "''"), song_titles))
    song_lyrics = list(map(lambda x: x.replace("'", "''"), song_lyrics))
    comment = comment.replace("'", "''")

    conn = psycopg2.connect(connection_info)
    cursor = conn.cursor()

    try:
      # date 테이블에서 현재 날짜에 해당하는 id 조회
      cursor.execute(f"""
            SELECT id FROM date WHERE year = {year} AND month = {month} AND day = {day};
        """)
      result = cursor.fetchone()

      if result is not None: # 바꿔치기
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
                UPDATE recommend SET 
                music1 = '{song_titles[0]}',
                artist1 = '{song_artists[0]}',
                music2 = '{song_titles[1]}',
                artist2 = '{song_artists[1]}',
                music3 = '{song_titles[2]}',
                artist3 = '{song_artists[2]}',
                music4 = '{song_titles[3]}',
                artist4 = '{song_artists[3]}',
                music5 = '{song_titles[4]}',
                artist5 = '{song_artists[4]}',
                music6 = '{song_titles[5]}',
                artist6 = '{song_artists[5]}',
                music7 = '{song_titles[6]}',
                artist7 = '{song_artists[6]}',
                music8 = '{song_titles[7]}',
                artist8 = '{song_artists[7]}',
                music9 = '{song_titles[8]}',
                artist9 = '{song_artists[8]}',
                music10 = '{song_titles[9]}',
                artist10 = '{song_artists[9]}',
                music11 = '{song_titles[10]}',
                artist11 = '{song_artists[10]}',
                music12 = '{song_titles[11]}',
                artist12 = '{song_artists[11]}'
                WHERE id = {id};
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
            INSERT INTO recommend(id, music1, artist1, music2, artist2, music3, artist3) 
            VALUES ({id}, '{song_titles[0]}', '{song_artists[0]}', '{song_titles[1]}', '{song_artists[1]}', '{song_titles[2]}', '{song_artists[2]}');
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
    
    st.header("Cheer up 🫂")
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
                SELECT content FROM comment WHERE id = {id};
            """)        
        result = cursor.fetchone()
        if result is not None:
            content = result[0]
            st.write(f"{content}")
        else:
            st.write("오늘의 위로가 없습니다.")  
    except Exception as e:
        st.error("코멘트를 가져오는 중에 오류가 발생했습니다")
        st.error(e)
    finally:
        conn.close()
        
    with col1:
        st.header("Playlist 🎧")
        st.image('https://img.freepik.com/vetores-premium/design-de-vetor-simples-do-music-player-com-faixa-de-botoes-e-interface-de-player-de-audio-de-titulo_505988-666.jpg')
    with col2: # 여기에 추천노래 들어갈 것!
        st.header("")
        index = 0
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
                    SELECT music1, artist1, music2, artist2, music3, artist3 FROM recommend WHERE id = {id};
                """)
            result = cursor.fetchone()
            if result is not None and all(result):
                music1, artist1, music2, artist2, music3, artist3 = result
                st.write(f"1. {artist1} - {music1}")
                st.write(f"2. {artist2} - {music2}")
                st.write(f"3. {artist3} - {music3}")

                if st.button("다시 추천받고 싶어요 👎"):
                    index += 3
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
                                SELECT music{index+1}, artist{index+1}, music{index+2}, artist{index+2}, music{index+3}, artist{index+3} FROM recommend WHERE id = {id};
                            """)
                        result = cursor.fetchone()
                        if result is not None and all(result):
                            music1, artist1, music2, artist2, music3, artist3 = result
                            st.write(f"{index+1}. {artist1} - {music1}")
                            st.write(f"{index+2}. {artist2} - {music2}")
                            st.write(f"{index+3}. {artist3} - {music3}")
                        
                    except Exception as e:
                        st.error("더는 준비된 노래가 없습니다.")
                        st.error(e)
            else:
                st.write("추천된 노래가 없습니다.")
        except Exception as e:
            st.error("추천된 노래를 가져오는 중에 오류가 발생했습니다.")
            st.error(e)
        finally:
            conn.close()
        
        

    st.header("Today's record 🖋️")
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
    st.header("Past diary 🖋️")
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
    
    try:
        connection_info = "host=147.47.200.145 dbname=teamdb8 user=team8 password=youngjoon port=34543"
        conn = psycopg2.connect(connection_info)
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
    print(dates_and_emotions)
    dates_by_date = [date(date_[0],date_[1], date_[2]) for date_ in dates_and_emotions]
    # emotion_by_date = list(map(emo2idx, [emo[3] for emo in dates_and_emotions]))
    emotion_by_date = [emo[3] for emo in dates_and_emotions]

    df = pd.DataFrame({'Date':dates_by_date, 'Emotion': emotion_by_date, 'y': [1]*len(dates_by_date)})

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

    st.pyplot(fig)
        
    st.header("Cheer up 🫂")
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
                SELECT content FROM comment WHERE id = {id};
            """)        
        result = cursor.fetchone()
        if result is not None:
            content = result[0]
            st.write(f"{content}")
        else:
            st.write(f"{selected_date}의 기록이 없습니다.")  
    except Exception as e:
        st.error("코멘트를 가져오는 중에 오류가 발생했습니다")
        st.error(e)
    finally:
        conn.close()
        
    with col3:
        st.header("Playlist 🎧")
        st.image('https://img.freepik.com/vetores-premium/design-de-vetor-simples-do-music-player-com-faixa-de-botoes-e-interface-de-player-de-audio-de-titulo_505988-666.jpg')

    with col4: 
        st.header("")
        try:
            conn = psycopg2.connect(connection_info)
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT id FROM date WHERE year = {selected_year} AND month = {selected_month} AND day = {selected_day};
            """)
            
            result = cursor.fetchone()
            print(result)
            if result is not None:
                id = result[0]
                cursor.execute(f"""
                    SELECT music1, artist1, music2, artist2, music3, artist3 FROM recommend WHERE id = {id};
                """)
            result = cursor.fetchone()
            if result is not None and all(result):
                music1, artist1, music2, artist2, music3, artist3 = result
                st.write(f"1. {artist1} - {music1}")
                st.write(f"2. {artist2} - {music2}")
                st.write(f"3. {artist3} - {music3}")
            else:
                st.write("추천된 노래가 없습니다.")
        except Exception as e:
            st.error("추천된 노래를 가져오는 중에 오류가 발생했습니다.")
            st.error(e)
        finally:
            conn.close()
            

    