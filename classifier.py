import pinecone, torch, torch.nn as nn
from transformers import RobertaTokenizer, RobertaModel, RobertaConfig, pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Redefine classifier layer
# source code: https://github.com/huggingface/transformers/blob/84ea427f460ffc8d2ddc08a341ccda076c24fc1f/src/transformers/models/roberta/modeling_roberta.py#L1443
# config: https://huggingface.co/michellejieli/emotion_text_classifier/blob/main/config.json

class RobertaClassificationHead(nn.Module):
    """Head for sentence-level classification tasks."""

    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        classifier_dropout = (
            config.classifier_dropout if config.classifier_dropout is not None else config.hidden_dropout_prob
        )
        self.dropout = nn.Dropout(classifier_dropout)
        self.out_proj = nn.Linear(config.hidden_size, 28) # config.num_labels

    def forward(self, features, **kwargs):
        # x = features[:, 0, :]  # take <s> token (equiv. to [CLS])
        x = features
        x = self.dropout(x)
        x = self.dense(x)
        x = torch.tanh(x)
        x = self.dropout(x)
        x = self.out_proj(x)
        return x
    
class Classifier:
    def __init__(self):
        # vars
        self.total_score = 0.0
    
    def __call__(self, diary_text: str):    
       

        ## textual embedding
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.diary_text_embedding = model.encode(diary_text) # d: 384, dtype: torch FloatTensor

        ## emotional embedding
        config = RobertaConfig.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
        config.output_hidden_states = True
        config.num_labels = 7
        tok = RobertaTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
        diary_text_emb = tok.encode(diary_text, return_tensors='pt')
        model = RobertaModel.from_pretrained("j-hartmann/emotion-english-distilroberta-base", config=config)
        self.diary_emo_embedding = model(diary_text_emb).pooler_output.squeeze().detach().numpy() # d: 786, dtype: torch FloatTensor

        # get emotion score and classify
        self.classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)
        label_scores = self.classifier(diary_text)[0]
        max_score_label = max(label_scores, key=lambda x: x['score'])
        self.diary_emotion = max_score_label['label']
        if self.diary_emotion in ['anger','disgust','fear','sadness']: # anger, disgust, fear, sadness
            self.diary_emotion_scores = 0
        elif self.diary_emotion in ['joy']: # joy
            self.diary_emotion_scores = 1
        else: # neutral, surprise
            self.diary_emotion_scores = 2
        
        return self.diary_emotion, self.diary_emotion_scores


    def compute_scores(self, max_k=100, include_values = True):

        # get score
        s1_scores, selected_ids = self.compute_s1(max_k, include_values)
        s2_scores = self.compute_s2(selected_ids)

        # scaling
        total_score = s1_scores * 0.5 + s2_scores * 0.5 # s1_scores.shape: (1,100), s2_scores.shape: (1,100)
        selected_ids = list(map(lambda x: int(x), selected_ids))
        return total_score, selected_ids


    def compute_s1(self, max_k = 100, include_values = True):
        '''
        compute similarity score (1) between diary textual embedding and lyrics textual embedding.
        The dimension of both embeddings is 384.
        '''
        API_KEY = "12dfbe87-05b3-4243-bb22-e69d329f18ed"
        ENVIRONMENT = "gcp-starter"
        pinecone.init(api_key = API_KEY, environment = ENVIRONMENT)
        pinecone_db_lyrics_text = pinecone.Index('textual')
        # Retrieve
        s1 = pinecone_db_lyrics_text.query(
        vector=self.diary_text_embedding.tolist(),
        top_k=max_k,
        include_values = include_values
        )['matches'] # [{id,score,value}, {id,score,value}...]

        # s1_vecs = {} # {id1: value, id2: value, ...}
        s1_scores = [] # {id1: s1_score, id2: s1_score, ...}
        selected_ids = []

        for element in s1:
            # s1_vecs[element['id']] = torch.tensor(element['value'])
            s1_scores.append(torch.tensor(element['score']))
            selected_ids.append(element['id'])

        s1_scores = torch.stack(s1_scores).reshape(1, -1) # 1 x 100 (max_k)

        return s1_scores, selected_ids
        
    def compute_s2(self, selected_ids):
        '''
        compute similarity score (2) the sum of s1 main and s2 sub. Each of them scales to the ranges of [0, 0.375] and [0, 0.125].
        '''
        s2_main_score = self.compute_s2_main(selected_ids=selected_ids)
        s2_sub_score = self.compute_s2_sub(selected_ids=selected_ids)
        return s2_main_score * 0.75 + s2_sub_score * 0.25
        

    def compute_s2_main(self, selected_ids, include_values = True):
        '''
        compute similarity score between diary emotion embedding and lyrics emotion embedding.
        The dimension of both embeddings is 786.
        It scales to [0, 0.375].
        '''
        
        API_KEY = 'be8c134a-92af-4f8c-ae2c-a2cc127d17f0'
        ENVIRONMENT = "gcp-starter"
        pinecone.init(api_key = API_KEY, environment = ENVIRONMENT)
        pinecone_db_lyrics_emo = pinecone.Index('emotion')
        
        # Retrieve
        s2_main = [] # 100
        
        for id in selected_ids:
            s2_main.append(pinecone_db_lyrics_emo.query(
                id=id,
                include_values = include_values,
                top_k=1
            )['matches'][0]['values']) # [embs, embs, ...], (100, 768)
        
        s2_main = torch.FloatTensor(s2_main) # (100,768)

        s2_main_score = cosine_similarity(self.diary_emo_embedding.reshape(1,-1), s2_main)
        
        return s2_main_score # (1,768) x (768, 100) =>  1 x 100 

    def compute_s2_sub(self, selected_ids, include_values = True):
        '''
        indicator function for music feature. 
        if the music feature label (0,1,2) matches the query emotion label (0,1,2), then 1 otherwise 0.
        It scalse to [0, 0.125]
        '''
        API_KEY = "17adaef6-2910-47b3-bcfb-7735e7d51384"
        ENVIRONMENT = "gcp-starter"
        pinecone.init(api_key = API_KEY, environment = ENVIRONMENT)
        pinecone_db_features = pinecone.Index('emotionmusicfeatures')
        # Retrieve
        s2_sub = [] # 100

        for id in selected_ids:
            s2_sub.append(pinecone_db_features.query(
                id=id,
                include_values = include_values,
                top_k=1
            )['matches'][0]['values']) # [label, label, ...] (100,1)

        s2_sub = torch.FloatTensor(s2_sub).reshape(1,100) # (1,100)
        s2_sub = torch.eq(torch.ones(s2_sub.shape[1])*self.diary_emotion_scores, s2_sub)*1
        s2_sub = s2_sub.detach().numpy()
        
        return s2_sub # (1,100)
             
    
    def return_topk_music(self, scores, selected_ids, top_k=5):
        idxs = torch.topk(scores, k=top_k).indices.detach().numpy().astype(int)
        idxs = np.array(idxs)
        selected_ids = np.array(selected_ids)
        topk_music_ids = selected_ids[idxs]
        
        return topk_music_ids