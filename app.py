import streamlit as st
import pickle
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    st.error("Bearer token not loaded. Please check your .env file.")
    st.stop()

# Streamlit Config
st.set_page_config(page_title="🎬 CineMatch - Movie Recommender", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        html, body {
            background-color: #f0f2f6;
            font-family: 'Segoe UI', sans-serif;
        }
        .banner {
            background: linear-gradient(90deg, #141e30, #243b55);
            color: white;
            padding: 3rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
        }
        .banner h1 {
            font-size: 3rem;
            font-weight: 800;
        }
        .banner p {
            font-size: 1.2rem;
            margin-top: 1rem;
        }
        .movie-card {
            background-color: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.1);
            padding: 1rem;
            text-align: center;
        }
        .movie-card img {
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        .movie-card h4 {
            font-size: 1rem;
            color: #333;
        }
        .btn-recommend {
            background: linear-gradient(to right, #ff416c, #ff4b2b);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: bold;
            border: none;
        }
        .footer {
            text-align: center;
            padding: 2rem 0 1rem;
            color: #999;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)


# API to fetch poster
# Fetch movie details from TMDB
def fetch_movie_details(movie_id):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    # Movie details
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"

    movie_data = requests.get(movie_url, headers=headers).json()
    credits_data = requests.get(credits_url, headers=headers).json()

    poster = "https://image.tmdb.org/t/p/w500" + movie_data.get('poster_path', "") if movie_data.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Image"
    overview = movie_data.get("overview", "Overview not available.")
    genres = ", ".join([genre["name"] for genre in movie_data.get("genres", [])])
    cast = ", ".join([cast["name"] for cast in credits_data.get("cast", [])[:3]])

    return poster, overview, genres, cast


# Recommender logic
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    details = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, overview, genres, cast = fetch_movie_details(movie_id)
        details.append({
            "title": title,
            "poster": poster,
            "overview": overview,
            "genres": genres,
            "cast": cast
        })
    return details


# Load model and data
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# App Banner
# App Banner
st.markdown("""
<div class="banner">
    <h1>🎬 CineMatch</h1>
    <p>
        Your personal AI-powered movie recommender system.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar Section
with st.sidebar:
    st.header("🔍 Find Your Movie Match")
    selected_movie_name = st.selectbox("Pick a movie to base recommendations on:", movies['title'].values)
    recommend_clicked = st.button("🎯 Recommend", key="recommend")

    # Beautiful Quote
    st.markdown("""
        <div style='margin-top: 30px; padding: 10px; background-color: #fff8f0; border-left: 4px solid #ff4b2b; border-radius: 5px; font-style: italic; color: #444; font-size: 14px;'>
            🎥 "Cinema is a mirror by which we often see ourselves." – Alejandro González Iñárritu
        </div>
    """, unsafe_allow_html=True)

    # Publisher credit
    st.markdown("""
        <div style='margin-top: 50px; font-size: 12px; color: grey; text-align: center;'>
            Developed by <strong>NIKHILESH K</strong>
        </div>
    """, unsafe_allow_html=True)



# Recommend and Display
if recommend_clicked:
    recommendations = recommend(selected_movie_name)
    st.subheader(f"📽 Top Recommendations Based on: *{selected_movie_name}*")

    for movie in recommendations:
        with st.container():
            cols = st.columns([1, 2])
            with cols[0]:
                st.image(movie["poster"], width=180)
            with cols[1]:
                st.markdown(f"### 🎞 {movie['title']}")
                st.markdown(f"**Genres:** {movie['genres']}")
                st.markdown(f"**Top Cast:** {movie['cast']}")
                st.markdown(f"**Overview:** {movie['overview']}")
            st.markdown("---")


# Footer
st.markdown("""
<div class="footer">
    © 2025 CineMatch | All rights reserved. <br>Created by <strong>NIKHILESH K</strong>
</div>
""", unsafe_allow_html=True)


