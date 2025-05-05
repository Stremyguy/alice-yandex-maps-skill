from flask import Flask, request, jsonify
from typing import Optional
import logging
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    "москва": ["1652229/5a2b3f64bb49bf9d762d", "13200873/147fb7857d1556b9c81c"],
    "нью-йорк": ["1652229/9487e851b99277d0c8d2", "1533899/1f37db77b17051ff19fc"],
    "париж": ["1652229/e63f4d34bafba01c4d9d", "1652229/0a68aef7beb2ffe6b1b9"],
}

sessionStorage = {}


@app.route("/", methods=["GET", "POST"])
def main() -> dict:
    if request.method == "GET":
        return "Server is running!", 200
    
    logging.info(f"Request: {request.json!r}")
    
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
    
    res["response"]["buttons"] = [
        {"title": "Помощь", "hide": True}
    ]
    
    if req["session"]["new"]:
        res["response"]["text"] = "Привет! Назови свое имя!"
        sessionStorage[user_id] = {
            "first_name": None,
            "game_started": False
        }
        return

    if sessionStorage[user_id]["first_name"] is None:
        if "помощь" in req["request"]["nlu"]["tokens"]:
            res["response"]["text"] = "Тебе надо отгадать город по отправленной фотке.\nСейчас тебе надо отправить своё имя!"
        else:
            first_name = get_first_name(req)
            
            if first_name is None:
                res["response"]["text"] = \
                    "Не расслышала имя. Повтори, пожалуйста!"
            else:
                sessionStorage[user_id]["first_name"] = first_name
                sessionStorage[user_id]["guessed_cities"] = []
                res["response"]["text"] = f"Приятно познакомиться, {first_name.title()}. Я - Алиса. Отгадаешь город по фото?"
                res["response"]["buttons"] = [
                    {"title": "Да", "hide": True},
                    {"title": "Нет", "hide": True},
                    {"title": "Помощь", "hide": True},
                ]
    else:
        if not sessionStorage[user_id]["game_started"]:
            if "да" in req["request"]["nlu"]["tokens"]:
                if len(sessionStorage[user_id]["guessed_cities"]) == 3:
                    res["response"]["text"] = "Ты отгадал все города!"
                    res["end_session"] = True
                else:
                    sessionStorage[user_id]["game_started"] = True
                    sessionStorage[user_id]["attempt"] = 1
                    play_game(res, req)
            elif "нет" in req["request"]["nlu"]["tokens"]:
                res["response"]["text"] = "Ну и ладно!"
                res["end_session"] = True
            elif "помощь" in req["request"]["nlu"]["tokens"]:
                res["response"]["text"] = "Тебе надо отгадать город по отправленной фотке.\nДля начала игры напиши 'да'."
            else:
                res["response"]["text"] = "Не поняла ответа! Так да или нет?"
                res["response"]["buttons"] = [
                    {"title": "Да", "hide": True},
                    {"title": "Нет", "hide": True},
                ]
        else:
            play_game(res, req)


def play_game(res: dict, req: dict) -> None:
    user_id = req["session"]["user_id"]
    attempt = sessionStorage[user_id]["attempt"]
    
    res["response"]["buttons"] = [
        {"title": "Помощь", "hide": True}
    ]
    
    if "помощь" in req["request"]["nlu"]["tokens"]:
        res["response"]["text"] = "Тебе надо отгадать город по отправленной фотке.\nВводи ответ!"
    else:
        if attempt == 1:
            city = random.choice(list(cities))
            while city in sessionStorage[user_id]["guessed_cities"]:
                city = random.choice(list(cities))
            sessionStorage[user_id]["city"] = city
            res["response"]["card"] = {
                "type": "BigImage",
                "title": "Что это за город?",
                "image_id": cities[city][attempt - 1]
            }
            res["response"]["text"] = "Тогда сыграем!"
        else:
            city = sessionStorage[user_id]["city"]
            if get_city(req) == city:
                res["response"]["text"] = "Правильно! Сыграем ещё?"
                sessionStorage[user_id]["guessed_cities"].append(city)
                sessionStorage[user_id]["game_started"] = False
                return
            else:
                if attempt == 3:
                    res["response"]["text"] = f"Вы пытались. Это {city.title()}. Сыграем ещё?"
                    sessionStorage[user_id]["game_started"] = False
                    sessionStorage[user_id]["guessed_cities"].append(city)
                    return
                else:
                    res["response"]["card"] = {
                        "type": "BigImage",
                        "title": "Неправильно. Вот тебе дополнительное фото",
                        "image_id": cities[city][attempt - 1]
                    }
                    res["response"]["text"] = "А вот и не угадал!"
        sessionStorage[user_id]["attempt"] += 1


def get_city(req: dict) -> Optional[str]:
    for entity in req["request"]["nlu"]["entities"]:
        if entity["type"] == "YANDEX.GEO":
            return entity["value"].get("city", None)


def get_first_name(req: dict) -> Optional[str]:
    for entity in req["request"]["nlu"]["entities"]:
        if entity["type"] == "YANDEX.FIO":
            return entity["value"].get("first_name", None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
