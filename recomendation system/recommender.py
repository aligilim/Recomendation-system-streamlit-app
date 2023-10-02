import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

def get_recommended_games(df, game_name):
    # Combine the values of the important columns into a single string
    def get_important_features(data):
        important_features = []
        for i in range(0, data.shape[0]):
            important_features.append(data['steamspy_tags'][i] + ' ' + data['name'][i])

        return important_features
    
    df = df[df['positive_ratings'] > 50]
    df = df.reset_index(drop = True)
    df['important_features'] = get_important_features(df)
    df['Game_no'] = range(0,df.shape[0])
    # Convert to matrix
    cm = CountVectorizer().fit_transform(df['important_features'])

    # Get the cosine similarity matrix from cm
    cs = cosine_similarity(cm)

    # Find the appid
    app_id = df[df.name == game_name]['Game_no'].values[0]

    # Create a list of similarity score
    scores = list(enumerate(cs[app_id]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = scores[1:]  # Remove the first score (self)
    
    df['positive_ratings'] = df['positive_ratings'].astype(str)

    # Prepare the recommendations
    recommended_games = []
    for item in scores[:20]:
        game_title = (
            df[df.Game_no == item[0]]['name'].values[0]
            + ' (Positive Ratings : '
            + df[df.Game_no == item[0]]['positive_ratings'].values[0]
            + ')'
        )
        recommended_games.append(game_title)

    return recommended_games
