from flask import Flask, request, jsonify
from geo import get_country, get_distance, get_coordinates
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename="app.log",
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")


@app.route("/", methods=["GET", "POST"])
def main() -> dict:
    if request.method == "GET":
        return "Server is running!", 200
    
    logging.info(f"Request: %r", request.json)
    
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {
            "end_session": False,
            "text": ""
        }
    }
    handle_dialogue(response, request.json)
    logging.info(f"Response: %r", response)
    return jsonify(response)


def handle_dialogue(res: dict, req: dict) -> None:
    if req["session"]["new"]:
        res["response"]["text"] = \
            "Привет! Я могу показать город или сказать расстояние между городами!"
        return
    
    cities = get_cities(req)
    
    if not cities:
        res["response"]["text"] = "Ты не написал название ни одного города!"
    elif len(cities) == 1:
        res["response"]["text"] = f"Этот город в стране - {get_country(cities[0])}"
    elif len(cities) == 2:
        distance = get_distance(get_coordinates(cities[0]), get_coordinates(cities[1]))
        res["response"]["text"] = f"Расстояние между этими городами: {str(round(distance))} км."
    else:
        res["response"]["text"] = "Слишком много городов!"


def get_cities(req: dict) -> list:
    cities = []
    for entity in req["request"]["nlu"]["entities"]:
        if entity["type"] == "YANDEX.GEO":
            if "city" in entity["value"]:
                cities.append(entity["value"]["city"])
    return cities


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
