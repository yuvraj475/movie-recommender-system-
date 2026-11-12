
import streamlit as st
import pickle
import requests

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)


# ---------------- LOAD DATA ----------------

@st.cache_resource
def load_data():

    with open("movie_list.pkl", "rb") as file:
        movies = pickle.load(file)

    with open("top_movies.pkl", "rb") as file:
        top_movies = pickle.load(file)

    return movies, top_movies


movies, top_movies = load_data()


# ---------------- TMDB API KEY ----------------

API_KEY = st.secrets["TMDB_API_KEY"]


# ---------------- RECOMMENDATION FUNCTION ----------------

def recommend(movie):

    movie_index = movies[
        movies["title"] == movie
    ].index[0]

    movie_indices = top_movies[movie_index]

    recommended_movies = []

    for idx in movie_indices[:5]:

        movie_id = movies.iloc[idx]["movie_id"]
        movie_title = movies.iloc[idx]["title"]

        recommended_movies.append(
            (movie_id, movie_title)
        )

    return recommended_movies


# ---------------- FETCH MOVIE DETAILS ----------------

@st.cache_data(ttl=86400)
def fetch_movie_details(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": API_KEY
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return None

    except requests.RequestException:
        return None


# ---------------- MAIN APP UI ----------------

st.title("🎬 Movie Recommendation System")

st.write(
    "Find your next favourite movie based on your selected movie!"
)

st.divider()


# ---------------- MOVIE SELECTBOX ----------------

selected_movie = st.selectbox(
    "🔍 Search or Select a Movie",
    movies["title"].values
)


# ---------------- RECOMMENDATION BUTTON ----------------

if st.button("🍿 Recommend Movies", type="primary"):

    recommendations = recommend(selected_movie)

    st.subheader(
        f"Movies Similar to {selected_movie}"
    )

    cols = st.columns(5)

    for col, (movie_id, movie_title) in zip(
        cols,
        recommendations
    ):

        details = fetch_movie_details(movie_id)

        with col:

            if details:

                # Movie Poster
                poster = details.get("poster_path")

                if poster:

                    image_url = (
                        "https://image.tmdb.org/t/p/w500"
                        + poster
                    )

                    st.image(
                        image_url,
                        use_container_width=True
                    )

                else:
                    st.write("🖼️ Poster not available")

                # Movie Title
                st.markdown(f"**{movie_title}**")

                # Movie Rating
                rating = details.get(
                    "vote_average", 0
                )

                st.write(f"⭐ {rating:.1f}/10")

                # Movie Overview
                with st.expander("📖 Movie Overview"):

                    overview = details.get(
                        "overview",
                        "No overview available"
                    )

                    st.write(
                        overview if overview
                        else "No overview available"
                    )

            else:

                st.markdown(f"**{movie_title}**")
                st.caption("Movie details unavailable")

