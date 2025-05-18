import logging
from flask import Flask, request, jsonify
from geo import get_country, get_distance, get_coordinates
from typing import Optional

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename="app.log",
                    format="%(asctime)s %(levelname)s %(name)s %(message)s")

sessionStorage = {}

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
    user_id = req["session"]["user_id"]
    
    if req["session"]["new"]:
        sessionStorage[user_id] = {
            "first_name": None,
            "suggests": [
                "Помощь",
            ]
        }
        res["response"]["text"] = "Привет! Как тебя зовут?"
        res["response"]["buttons"] = get_suggests(user_id)
        return
    
    if sessionStorage[user_id]["first_name"] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res["response"]["text"] = "Не расслышала имя. Повтори, пожалуйста!"
            res["response"]["buttons"] = get_suggests(user_id)
        else:
            sessionStorage[user_id]["first_name"] = first_name
            res["response"]["text"] = f"Приятно познакомиться, {first_name.title()}! Я могу показать город или сказать расстояние между городами!"
            res["response"]["buttons"] = get_suggests(user_id)
        return

    cities = get_cities(req)
    
    if not cities:
        res["response"]["text"] = f"{sessionStorage[user_id]['first_name'].title()}, ты не написал название ни одного города!"
        res["response"]["buttons"] = get_suggests(user_id)
    elif len(cities) == 1:
        country = get_country(cities[0])
        res["response"]["text"] = f"{sessionStorage[user_id]['first_name'].title()}, этот город находится в стране - {country}"
        res["response"]["buttons"] = get_suggests(user_id)
    elif len(cities) == 2:
        try:
            distance = get_distance(get_coordinates(cities[0]), get_coordinates(cities[1]))
            res["response"]["text"] = f"{sessionStorage[user_id]['first_name'].title()}, расстояние между этими городами: {str(round(distance))} км."
            res["response"]["buttons"] = get_suggests(user_id)
        except Exception as e:
            logging.error(f"Ошибка рассчёта дистанции: {e}")
            res["response"]["text"] = f"{sessionStorage[user_id]['first_name'].title()}, произошла ошибка при расчете расстояния. Попробуйте другие города."
            res["response"]["buttons"] = get_suggests(user_id)
    else:
        res["response"]["text"] = f"{sessionStorage[user_id]['first_name'].title()}, слишком много городов! Максимум 2."
        res["response"]["buttons"] = get_suggests(user_id)


def get_cities(req: dict) -> list:
    cities = []
    for entity in req["request"]["nlu"]["entities"]:
        if entity["type"] == "YANDEX.GEO":
            if "city" in entity["value"]:
                cities.append(entity["value"]["city"])
    return cities


def get_first_name(req: dict) -> Optional[str]:
    for entity in req["request"]["nlu"]["entities"]:
        if entity["type"] == "YANDEX.FIO":
            return entity["value"].get("first_name", None)
    return None


def get_suggests(user_id: str) -> list:
    session = sessionStorage[user_id]
    suggests = []
    for suggest in session["suggests"]:
        suggests.append({
            "title": suggest,
            "hide": True
        })
    return suggests


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
