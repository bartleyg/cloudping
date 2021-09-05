from flask import Flask, g, request, jsonify
import json

from database import get_db


app = Flask(__name__)


# close database connection after requests
@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/api/pings", methods=["OPTIONS"])
@app.route("/api/endpoints", methods=["OPTIONS"])
def options():
    # Set CORS headers for the preflight request
    # Allows POST, PUT, GET, DELETE, OPTIONS requests from any origin with the Content-Type
    # header and caches preflight response for an 3600s
    print("options")
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
    }
    return "", 204, headers


@app.post("/api/pings")
def post_pings():
    payload = request.get_json()
    print("POST /api/pings received payload:", json.dumps(payload, indent=4))
    # validate list
    if type(payload) != list or len(payload) == 0:
        return ("payload not list or is empty", 400)
    # validate keys for each object in list
    required_keys = ["user", "type", "endpoint_id", "duration"]
    for obj in payload:
        for k in required_keys:
            if k not in obj:
                return (f"payload obj missing key '{k}'", 400)
    sql = """
        WITH ROW AS (
        	INSERT INTO pings ("user", "type") VALUES (%s, %s) RETURNING id
        )
        INSERT INTO results ("ping_id", "endpoint_id", "duration") VALUES (
        	(SELECT id FROM ROW),
        	%s,
        	%s
        );
    """
    with get_db().cursor() as cur:
        for obj in payload:
            cur.execute(
                sql,
                [
                    obj["user"],
                    obj["type"],
                    obj["endpoint_id"],
                    obj["duration"],
                ],
            )
    # set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}
    return "OK", 200, headers


@app.get("/api/pings")
def get_pings():
    print("GET /api/pings")
    # fetch from db view
    with get_db().cursor() as cur:
        cur.execute("SELECT * FROM all_pings LIMIT 50;")
        pings = cur.fetchall()
    # set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}
    return jsonify(pings), 200, headers


@app.get("/api/endpoints")
def get_endpoints():
    with get_db().cursor() as cur:
        cur.execute("SELECT * FROM endpoints;")
        endpoints = cur.fetchall()
    print("endpoints:", json.dumps(endpoints, indent=4))
    # set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}
    return jsonify(endpoints), 200, headers


@app.get("/")
def index():
    return "OK", 200


if __name__ == "__main__":
    app.run("0.0.0.0", 80)
