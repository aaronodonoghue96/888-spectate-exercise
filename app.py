"""
A CRUD REST API for viewing, creating, deleting, and updating sports,
events for each sport, and selections for each event
"""

import sqlite3
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from dateutil.parser import parse
from dateutil.tz import UTC
from slugify import slugify

app = Flask(__name__)

DATABASE = "app.db"

def init_db():

    """
    Initializes the database with the correct tables for sports,
    events and selections
    """

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS sports (
                        sport_id INTEGER PRIMARY KEY,
                        name TEXT,
                        slug TEXT,
                        active BOOLEAN
                    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS events (
                        event_id INTEGER PRIMARY KEY,
                        name TEXT,
                        slug TEXT,
                        active BOOLEAN,
                        type TEXT,
                        sport TEXT,
                        status TEXT,
                        scheduled_start TEXT,
                        actual_start TEXT,
                        FOREIGN KEY (sport)
                            REFERENCES sports (name)
                    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS selections (
                        selection_id INTEGER PRIMARY KEY,
                        name TEXT,
                        event TEXT,
                        price REAL,
                        active BOOLEAN,
                        outcome TEXT,
                        FOREIGN KEY (event)
                            REFERENCES events (name)
                    );""")
    
    conn.commit()
    conn.close()

def get_db_connection():

    """
    Get the database connection for persisting new records, updating,
    retrieving, or deleting existing records
    """

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=['GET'])
def hello():

    """
    Welcomes the user to the API, giving instructions on how to access records
    from any of the three tables
    """

    return """Welcome to the API! To search for sports, events or selections,
            add "sports", "events" or "selections" to the URL"""

@app.route("/sports", methods=['POST'])
def create_sport():

    """
    Create a new sport with a given name, and optionally a slug and active 
    status. If a slug is not provided, slugify will generate one from the
    name. If an active status is not provided, False will be assumed by
    default, as the sport is new, and thus has no ongoing events
    """

    try:
        name = request.args.get('name')
        slug = request.args.get('slug') or slugify(name)
        active = request.args.get('active') or False

        if not name:
            return jsonify({'error': "Name of sport is required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO sports (name, slug, active)
                        VALUES (?, ?, ?)""", (
            name,
            slug,
            active
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'sport created'}), 201
    except sqlite3.Error as e:
        return jsonify({'message': f'error creating sport: {e}'}), 500

@app.route("/sports", methods=['GET'])
def search_sports():
    data = request.args

    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT * FROM sports"

    params = []

    if len(data) != 0:
        query += " WHERE "
        for arg in data:
            # subquery to handle more complex query of getting sports 
            # with a certain minimum number of active events
            if arg == "minEvents":
                query += """name IN 
                            (SELECT sport FROM events GROUP BY sport 
                            HAVING SUM(active) >= ?) AND """
                params.append(int(data[arg]))
            elif arg.startswith("name-"):
                query += f"{arg} LIKE ? AND "
                param = data[arg]
                if arg == "name-start":
                    param = "%" + data[arg]
                elif arg == "name-end":
                    param = data[arg] + "%"
                elif arg == "name-contains":
                    param = "%" + data[arg] + "%"
                params.append(param)
            else:
                query += f"{arg} = ? AND "
                params.append(data[arg])
        query = query[:-4] # remove the last "AND"
        #params = " AND ".join([arg + " = " + data[arg] for arg in data])
        print(query, params)
        breakpoint()
        cur.execute(query, params)

    else:
        cur.execute(query)

    sports = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in sports]), 200

@app.route("/sports/<string:name>", methods=['PUT'])
def update_sport(name):
    data = request.args

    if len(data) == 0:
        return jsonify({'message': 'No data provided to update'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    update_fields = []
    update_params = []

    for arg in data:
        update_fields.append(f"{arg} = ?")
        update_params.append(data[arg])
    update_params.append(name)

    query = f"UPDATE sports SET {', '.join(update_fields)} WHERE name = ?"
    cur.execute(query, update_params)
    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated successfully'})

@app.route("/sports/<string:name>", methods=['DELETE'])
def delete_sport(name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sports WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return jsonify({'message': "sport deleted"}), 204

@app.route("/events", methods=['POST'])
def create_event():
    try:
        name = request.args.get('name')
        slug = request.args.get('slug') or slugify(name)
        active = request.args.get('active') or False
        event_type = request.args.get('type')
        sport = request.args.get('sport')
        # event must start as Pending, as it has not taken place yet
        status = "Pending"
        scheduled_start = parse(request.args.get('scheduled_start'))
        scheduled_start_utc = scheduled_start.astimezone(UTC)
        # this won't be set until the event type is changed to Started
        actual_start = "NULL"

        if not all([name, event_type, sport, scheduled_start]):
            create_event_message = """Name, type, sport and scheduled start
                                    of event are all required"""
            return jsonify({'error': create_event_message}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO events
                        (name, slug, active, type, sport, status, 
                        scheduled_start, actual_start)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
            name,
            slug,
            active,
            event_type,
            sport,
            status,
            scheduled_start_utc,
            actual_start
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'event created'}), 201
    except sqlite3.Error as e:
        return jsonify({'message': f'error creating event: {e}'}), 500

@app.route("/events", methods=['GET'])
def search_events():
    data = request.args

    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT * FROM events"

    params = []

    if len(data) != 0:
        query += " WHERE "
        for arg in data:
            # subquery to handle more complex query of getting events
            # with a certain minimum number of active selections
            if arg == "minSelections":
                query += """name IN (SELECT event FROM selections
                            GROUP BY selection
                            HAVING SUM(active) >= ?) AND """
                params.append(data[arg])
            elif arg == "timeframe":
                param = parse(data[arg])
                param_utc = param.astimezone(UTC)
                query += """scheduled_start BETWEEN DATETIME('now')
                            AND DATETIME(?) AND """
                params.append(param_utc)
            elif arg.startswith("name-"):   
                param = data[arg]
                if arg == "name-start":
                    param = "%" + data[arg]
                elif arg == "name-end":
                    param = data[arg] + "%"
                elif arg == "name-contains":
                    param = "%" + data[arg] + "%"
                query += f"{arg} LIKE ? AND "
                params.append(param)
            else:
                query += f"{arg} = ? AND "
                params.append(data[arg])
        #params = " AND ".join([arg + " = " + data[arg] for arg in data])
        query = query[:-4]        
        print(query, params)
        cur.execute(query, params)

    else:
        cur.execute(query)

    events = cur.fetchall()
    conn.close()
    if "scheduled_start" in data:
        sched_start = data["scheduled_start"]
        offset = sched_start[-5:]
        for row in events:
            row["scheduled_start"] = row["scheduled_start"].astimezone(offset)
        # convert time to timezone specified in request before displaying
    return jsonify([dict(row) for row in events]), 200

@app.route("/events/<string:name>", methods=['PUT'])
def update_event(name):
    data = request.args

    if len(data) == 0:
        return jsonify({'message': 'No data provided to update'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    update_fields = []
    update_params = []

    for arg in data:
        update_fields.append(f"{arg} = ?")
        update_params.append(data[arg])
    update_params.append(name)

    query = f"UPDATE events SET {', '.join(update_fields)} WHERE name = ?"
    cur.execute(query, update_params)

    active = data['active']
    status = data['status']

    # if the status is started,
    # the actual start should be set to the current time
    if status == "started":
        cur.execute("UPDATE events SET actual_start = ? WHERE name = ?",
                    (datetime.now(timezone.utc), name))
    elif status in ["ended", "cancelled"]:
        cur.execute("UPDATE events SET active = 0 WHERE name = ?", (name,))
    # for any update that deactivates an event,
    # check if it was the last one for its sport
    if active == "false" or status in ["ended", "cancelled"]:
        cur.execute("""UPDATE sports SET active = 0 WHERE name IN
                    (SELECT sport FROM events GROUP BY sport 
                    HAVING SUM(active) = 0)""")

    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated successfully'})

@app.route("/events/<string:name>", methods=['DELETE'])
def delete_event(name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return jsonify({'message': "event deleted"}), 204

@app.route("/selections", methods=['POST'])
def create_selection():
    try:
        name = request.args.get('name')
        event = request.args.get('event')
        price = request.args.get('price')
        active = request.args.get('active') or False
        # outcome will be Unsettled by default, as we don't know the result yet
        outcome = request.args.get('outcome') or "Unsettled"

        if not all([name, event, price]):
            return jsonify({'error': "Name, event and price of selection are required"}), 400

        print(request.args)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""INSERT INTO selections
                    (name, event, price, active, outcome)
                    VALUES (?, ?, ?, ?, ?)""", (
            name,
            event,
            price,
            active,
            outcome
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'selection created'}), 201
    except sqlite3.Error as e:
        return jsonify({'message': f'error creating selection: {e}'}), 500

@app.route("/selections", methods=['GET'])
def search_selections():
    data = request.args

    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT * FROM selections"

    params = []

    if len(data) != 0:
        query += " WHERE "
        for arg in data:
            if arg == "min_price":
                query += "price >= ? AND"
                params.append(data[arg])
            elif arg == "max_price":
                query += "price <= ? AND"
                params.append(data[arg])
            elif arg.startswith("name-"):
                param = data[arg]
                if arg == "name-start":
                    param = "%" + data[arg]
                elif arg == "name-end":
                    param = data[arg] + "%"
                elif arg == "name-contains":
                    param = "%" + data[arg] + "%"
                query += f"{arg} LIKE ? AND "
                params.append(param)
            else:
                query += f"{arg} = ? AND "
                params.append(data[arg])
        query = query[:-4]
        #params = " AND ".join([arg + " = " + data[arg] for arg in data])
        print(query, params)
        cur.execute(query, params)

    else:
        cur.execute(query)

    sports = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in sports]), 200

@app.route("/selections/<string:name>", methods=['PUT'])
def update_selection(name):
    data = request.args

    if len(data == 0):
        return jsonify({'message': 'No data provided to update'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    update_fields = []
    update_params = []

    for arg in data:
        update_fields.append(f"{arg} = ?")
        update_params.append(data[arg])

    update_params.append(name)

    query = f"UPDATE selections SET {', '.join(update_fields)} WHERE name = ?"
    cur.execute(query, update_params)

    outcome = data['outcome']
    active = data['active']

    # if the outcome is not unsettled, it is either a win, loss or void,
    # all of which mean the selection is inactive
    if outcome != "unsettled":
        cur.execute("UPDATE selections SET active = 0 WHERE name = ?", (name,))

    # if selection is set to inactive, and it was the last selection
    # for its event, set the event to inactive
    if active == "false" or outcome != "unsettled":
        cur.execute("""UPDATE events SET active = 0 WHERE name IN
                    (SELECT event FROM selections GROUP BY event 
                    HAVING SUM(active) = 0)""")
        # if the event was the last event for its sport,
        # the sport should also be inactive
        cur.execute("""UPDATE sports SET active = 0 WHERE name IN
                    (SELECT sport FROM events GROUP BY sport 
                    HAVING SUM(active) = 0)""")
    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated successfully'})

@app.route("/selections/<string:name>", methods=['DELETE'])
def delete_selection(name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM selections WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return jsonify({'message': "selection deleted"}), 204

if __name__ == '__main__':
    init_db()
    app.run()
