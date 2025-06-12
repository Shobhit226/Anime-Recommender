from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Load genres from file
genre_map = {}
with open("anime_genres.txt", "r", encoding="utf-8") as file:
    for line in file:
        name, gid = line.strip().split(":")
        genre_map[name.lower()] = gid.strip()

def get_kitsu_details(title):
    url = f"https://kitsu.io/api/edge/anime?filter[text]={title}"
    try:
        response = requests.get(url)
        data = response.json()
        if data["data"]:
            info = data["data"][0]["attributes"]
            return {
                "rating": info.get("ageRating", "N/A"),
                "status": info.get("status", "N/A"),
                "desc": info.get("synopsis", "No description.")
            }
    except:
        pass
    return {"rating": "N/A", "status": "N/A", "desc": "N/A"}

def get_recommendations(genre_name):
    genre_id = genre_map.get(genre_name.lower())
    if not genre_id:
        return [{"title": "Genre not supported.", "url": "#", "image": "", "score": "", "synopsis": ""}]

    url = f"https://api.jikan.moe/v4/anime?genres={genre_id}&limit=5&order_by=score&sort=desc"
    try:
        response = requests.get(url)
        data = response.json()
        anime_list = []
        for anime in data["data"]:
            kitsu_info = get_kitsu_details(anime.get("title"))
            anime_list.append({
                "title": anime.get("title"),
                "url": anime.get("url"),
                "image": anime["images"]["jpg"]["image_url"],
                "score": anime.get("score", "N/A"),
                "synopsis": kitsu_info["desc"],
                "rating": kitsu_info["rating"],
                "status": kitsu_info["status"],
                "type": anime.get("type", ""),
                "episodes": anime.get("episodes", "N/A"),
                "duration": anime.get("duration", "")
            })
        return anime_list
    except Exception as e:
        print("Error:", e)
        return [{"title": "Failed to load data.", "url": "#", "image": "", "score": "", "synopsis": ""}]

@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    genre = ""
    if request.method == "POST":
        genre = request.form["genre"]
        recommendations = get_recommendations(genre)
    return render_template("index.html", recommendations=recommendations, genre=genre)

if __name__ == "__main__":
    app.run(debug=True)
