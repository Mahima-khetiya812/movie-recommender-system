import streamlit as st
import pickle
import requests
import os

################################### CSS ########################################
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>

/* remove top whitespace */
.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
    padding-left:3rem;
    padding-right:3rem;
}

/* title styling */
.app-title{
    font-size:55px;
    font-weight:700;
    margin-bottom:5px;
}

.app-subtitle{
    color:#9ca3af;
    font-size:20px;
    margin-bottom:35px;
}

/* make button prettier */
.stButton > button{
    border-radius:12px;
    padding:0.6rem 1.5rem;
    font-size:16px;
    font-weight:600;
}

/* make selectbox bigger */
.stSelectbox label{
    font-size:18px !important;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

################################################################################



TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"

    response = requests.get(url, timeout=10)

    data = response.json()

    poster_path = data.get('poster_path')
    overview = data.get('overview', 'No overview available.')
    release_date = data.get('release_date', 'N/A')

    if poster_path:
        poster = f"https://image.tmdb.org/t/p/w500/{poster_path}"
    else:
        poster = "https://via.placeholder.com/500x750?text=No+Poster"

    return poster, overview, release_date

def recommend(movie):

    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    names = []
    posters = []
    overviews = []
    dates = []

    for i in movies_list:

        movie_id = movies.iloc[i[0]].movie_id

        poster, overview, release_date = fetch_movie_details(
            movie_id
        )

        names.append(movies.iloc[i[0]].title)
        posters.append(poster)
        overviews.append(overview)
        dates.append(release_date)

    return names, posters, overviews, dates

@st.cache_resource
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()
movie_list = movies["title"].values

left, right = st.columns([4,1])

with left:
    st.markdown("""
    <div class='app-title'>
    🎬 Movie Recommendation System
    </div>

    <div class='app-subtitle'>
    Find movies similar to your favourites.
    </div>
    """, unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    "Select a movie",
    movie_list,
)

if st.button("Recommend"):

    with st.spinner("🍿 Finding similar movies..."):
        names, posters, overviews, dates = recommend(
            selected_movie_name
        )

    st.success(
        f"Showing recommendations for: {selected_movie_name}"
    )

    cols = st.columns(5)

    for i in range(5):

        with cols[i]:

            st.image(
                posters[i],
                use_container_width=True
            )

            st.markdown(
                f"""
                <div class='movie-title'>
                    {names[i]}
                </div>

                <div class='movie-date'>
                    📅 {dates[i]}
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander("📝 Overview"):
                st.write(overviews[i])