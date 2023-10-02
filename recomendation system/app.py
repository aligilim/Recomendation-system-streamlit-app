import streamlit as st
import pandas as pd
import requests
import base64

# Import your recommender code from 'recommender.py'
from recommender import get_recommended_games

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)

# Load your data
df = pd.read_csv('usable_df.csv')

# Extract unique years from the release_date column
unique_years = pd.to_datetime(df['release_date']).dt.year.unique()
unique_years = sorted(unique_years)

# Extract and split the platform string, then create a list of unique platforms
df['platform'] = df['platforms'].apply(lambda x: x.split(';'))
unique_platforms = set([platform for platforms in df['platform'] for platform in platforms])

# Define the Streamlit app
def main():
    st.title("Steam Game Recommender")

    # Use 'sidebar' to add platform selection and sliders to the left side
    with st.sidebar:
        st.header("Platform Selection")
        # Add checkboxes for multi-platform selection
        selected_platforms = st.multiselect("Select Platforms", list(unique_platforms), default=list(unique_platforms))
        
        st.header("Filters")
        # Add a slider for filtering by rating
        min_rating = st.slider("Select Minimum Rating", min_value=0, max_value=10000, value=0)

        # Add a slider for choosing release year
        selected_year = st.slider("Select Release Year", min(unique_years), max(unique_years),
                                  (min(unique_years), max(unique_years)))

        # Add a slider for choosing maximum price
        max_price = st.slider("Select Maximum Price", min(df['price']), max(df['price']), max(df['price']), step=1.0)

    # User input
    game_name = st.selectbox("Select a game name:", df['name'].tolist())  # Display a dropdown list of game names

    if st.button("Recommend"):
        # Call your recommender function to get recommendations from the entire DataFrame
        all_recommendations = get_recommended_games(df, game_name)

        # Filter the recommendations based on the selected criteria (release year, maximum price, rating, and platforms)
        filtered_recommendations = []
        for i, recommendation in enumerate(all_recommendations):
            game_title = recommendation.split('(')[0].strip()  # Extract game title
            game_year = pd.to_datetime(df[df['name'] == game_title]['release_date']).dt.year.iloc[0]
            game_price = df[df['name'] == game_title]['price'].iloc[0]
            game_platforms = df[df['name'] == game_title]['platforms'].iloc[0]

            game_platforms = game_platforms.split(';')  # Split the platform string

            if (selected_year[0] <= game_year <= selected_year[1]) and (game_price <= max_price) \
                    and any(platform in selected_platforms for platform in game_platforms):
                        
                rating = float(recommendation.split(":")[-1].strip(")"))
                if rating >= min_rating:  # Filter by minimum rating
                    support_url = df[df['name'] == game_title]['support_url'].iloc[0]
                    image_url = df[df['name'] == game_title]['background'].iloc[0]
                    image_content = requests.get(image_url).content
                    image_base64 = base64.b64encode(image_content).decode('utf-8')
                    
                    # Modify the width attribute for smaller images (e.g., width='200px')
                    image_html = f"<a href='{support_url}' target='_blank'><img src='data:image/png;base64,{image_base64}' alt='{game_title}' width='120px'></a>"
                    filtered_recommendations.append((game_title, rating, image_html))

        # Display the filtered recommendations or a message if no games found
        st.subheader("Recommended Games:")

        if len(filtered_recommendations) == 0:
            st.write("No games found within the selected criteria for the provided game name.")
        else:
            # Create columns for each game recommendation (max 5 games per row)
            col_count = 5
            num_rows = len(filtered_recommendations) // col_count + 1
            
            max_name_length = max(len(game_title) for game_title, _, _ in filtered_recommendations)
            
            for row in range(num_rows):
                cols = st.columns(col_count)
                for i in range(col_count):
                    idx = row * col_count + i
                    if idx < len(filtered_recommendations):
                        game_title, rating, image_html = filtered_recommendations[idx]
                        cols[i].markdown(image_html, unsafe_allow_html=True)
                        cols[i].write(f"{game_title.ljust(max_name_length)}")
                        # cols[i].write(f"Rating: {rating}")

if __name__ == "__main__":
    main()
