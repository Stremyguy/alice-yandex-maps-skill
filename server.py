from flask import Flask, request, jsonify
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


@app.route("/post", methods=["POST"])
def main() -> dict:
    logging.info(f"Request: {request.json!r}")
    response = {
        "session": request.json["session"],
        "version": request.json["version"],
        "response": {
            "end_session": False
        }
    }
    handle_dialogue(response, request.json)
    logging.info(f"Response: {response!r}")
    return jsonify(response)


def handle_dialogue(res: dict, req: dict) -> None:
    user_id = req["session"]["user_id"]
    
    if req["session"]["new"]:
        res["response"]["text"] = "Привет! Назови свое имя!"
        sessionStorage[user_id] = {
            "first_name": None
        }
        return
    
    if sessionStorage[user_id]["first_name"] is None:
        first_name = get_first_name(req)
        
        if first_name is None:
            res["response"]["text"] = \
                "Не расслышала имя. Повтори, пожалуйста!"
        else:
            sessionStorage[user_id]["first_name"] = first_name
            res["response"][
                "text"] = "Приятно познакомиться, " \
                    + first_name.title() \
                    + ". Я - Алиса. Какой город хочешь увидеть?"
            res["response"]["buttons"] = [
                {
                    "title": city.title(),
                    "hide": True
                } for city in cities
            ]
    else:
        city = get_city(req)
        
        if city in cities:
            res["response"]["card"] = {}
            res["response"]["card"]["type"] = "BigImage"
            res["response"]["card"]["title"] = "Этот город я знаю."
            res["response"]["card"]["image_id"] = random.choice(cities[city])
        else:
            res["response"]["text"] = \
                "Первый раз слышу об этом городе. Попробуй еще разок!"


def get_city(req: dict) -> str | None:
    for entity in req["request"]["nlu"]["entities"]:
        if entity["type"] == "YANDEX.GEO":
            return entity["value"].get("city", None)


def get_first_name(req: dict) -> str | None:
    for entity in req["request"]["nlu"]["entities"]:
        if entity["type"] == "YANDEX.FIO":
            return entity["value"].get("first_name", None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
