"""
A CRUD REST API for viewing, creating, deleting, and updating sports,
events for each sport, and selections for each event
"""

import sqlite3
from datetime import datetime, timedelta, timezone
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
    conn.execute("PRAGMA foreign_keys = ON") # ensure foreign keys are enabled
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS sports (
                        name TEXT PRIMARY KEY,
                        slug TEXT,
                        active BOOLEAN
                    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS events (
                        name TEXT PRIMARY KEY,
                        slug TEXT,
                        active BOOLEAN,
                        type TEXT,
                        sport TEXT,
                        status TEXT,
                        scheduled_start TEXT,
                        actual_start TEXT,
                        FOREIGN KEY (sport)
                            REFERENCES sports (name)
                            ON UPDATE RESTRICT
                            ON DELETE RESTRICT
                    );""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS selections (
                        name TEXT PRIMARY KEY,
                        event TEXT,
                        price REAL,
                        active BOOLEAN,
                        outcome TEXT,
                        FOREIGN KEY (event)
                            REFERENCES events (name)
                            ON UPDATE RESTRICT
                            ON DELETE RESTRICT
                    );""")
    conn.commit()
    conn.close()

def get_db_connection():

    """
    Get the database connection for persisting new records, updating,
    retrieving, or deleting existing records
    """

    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON") # ensure foreign keys are enabled
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
        slug = request.args.get('slug')
        if name and not slug:
            slug = slugify(name)
        active = request.args.get('active') or False

        if type(active) == "str":
            if active.lower() in ["false", "0"]:
                active = False
            elif active.lower() in ["true", "1"]:
                active = True
            else:
                return jsonify({'error': "active must be either true or false"}), 400

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

    """
    Searches the sports table for all records, or when query parameters
    are specified, all records that match those criteria.

    Possible parameters:
    minEvents: gets all sports with a number of active events greater than
                or equal to the specified amount
    name-start: gets all sports whose name starts with the given string
    name-end: gets all sports whose name ends with the given string
    name-contains: gets all sports whose name contains the given string
                    anywhere in its name
    name: gets all sports whose name exactly matches the given string
    slug: gets all sports whose slug exactly matches the given slug
    active: gets all sports whose active status matches the given active
            status
    """

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
            if arg == "min-events":
                query += """name IN
                            (SELECT sport FROM events GROUP BY sport 
                            HAVING SUM(active) >= ?) AND """
                params.append(int(data[arg]))
            elif arg.startswith("name-"):
                query += "name LIKE ? AND "
                param = data[arg]
                if arg == "name-start":
                    param = data[arg] + "%"
                elif arg == "name-end":
                    param = "%" + data[arg]
                elif arg == "name-contains":
                    param = "%" + data[arg] + "%"
                params.append(param)

            # Avoid hardcoding parameters where possible, to make potential
            # updates for parameters for new columns in sports table easier
            # If it's not a parameter listed above, it should be one of the
            # columns in the sports table. Invalid parameters will result
            # in an error message
            else:
                arg = arg.replace("-", "_")
                query += f"{arg} = ? AND "
                params.append(data[arg])
        query = query[:-4] # remove the last "AND" from the query
        cur.execute(query, params)

    else:
        cur.execute(query)

    sports = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in sports]), 200

@app.route("/sports/<string:name>", methods=['PUT'])
def update_sport(name):

    """
    Updates the sport with the given name, setting new values in the
    database for each specified parameter.

    Possible Parameters:
    Slug: updates the slug in the database to the specified value in the query
            string
    Active: updates the active status in the database to the specified value
            in the query string
    
    Name cannot be updated because it is a primary key
    """

    data = request.args
    
    if 'active' in data.keys():
        active = data['active']

        if active.lower() == "false":
            active = False
        elif active.lower() == "true":
            active = True
        else:
            return jsonify({'error': "active must be either true or false"}), 400

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
    return jsonify({'message': 'Updated successfully'}), 200

@app.route("/sports/<string:name>", methods=['DELETE'])
def delete_sport(name):

    """
    Deletes a sport with the given name from the sports table
    """

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM sports WHERE name = ?", (name,))
    except sqlite3.Error as e:
        return jsonify({'error': f"error deleting sport: {e}"}, 500)
    conn.commit()
    conn.close()
    return jsonify({'message': "sport deleted"}), 204

@app.route("/events", methods=['POST'])
def create_event():

    """
    Create a new event with a given name, sport, scheduled start time, 
    and optionally a slug and active status. If a slug is not provided, 
    slugify will generate one from the name. If an active status is not 
    provided, False will be assumed by default, as the event is new, 
    and thus has no active selections
    """

    try:
        name = request.args.get('name')
        slug = request.args.get('slug')
        if name and not slug:
            slug = slugify(name)
        active = request.args.get('active') or False
        
        if type(active) == "str":
            if active.lower() in ["false", "0"]:
                active = False
            elif active.lower() in ["true", "1"]:
                active = True
            else:
                return jsonify({'error': "active must be either true or false"}), 400
            
        # the event has not taken place yet, play has not started, so
        # it should be Preplay until it is started.
        # Variable name is event_type to avoid confusion with Python's
        # 'type' function
        event_type = "Preplay"
        sport = request.args.get('sport')
        # event must start as Pending, as it has not taken place yet
        # so it can't be passed as a parameter, it makes no sense
        # to create an event after it's started (or ended, or been
        # cancelled)
        status = "Pending"
        scheduled_start = request.args.get('scheduled-start')
        if scheduled_start:
            scheduled_start = parse(scheduled_start)
            scheduled_start_utc = scheduled_start.astimezone(UTC)
        # this won't be set until the event type is changed to Started,
        # so it can't be passed as a parameter
        actual_start = "NULL"

        if not (name and sport and scheduled_start):
            create_event_message = "Name, type, sport and scheduled start "
            create_event_message += "of event are all required"
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

    """
    Searches the events table for all records, or when query parameters
    are specified, all records that match those criteria.

    Possible parameters:
    minSelections: gets all sports with a number of active selections greater
                   than or equal to the specified amount
    name-start: gets all sports whose name starts with the given string
    name-end: gets all sports whose name ends with the given string
    name-contains: gets all sports whose name contains the given string
                    anywhere in its name
    timeframe: gets all events that will occur between now and the specified
               date and time. May include offset for timezones
    name: gets all sports whose name exactly matches the given string
    slug: gets all sports whose slug exactly matches the given slug
    active: gets all sports whose active status matches the given active
            status
    """

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
            if arg == "min-selections":
                query += """name IN (SELECT event FROM selections
                            GROUP BY event HAVING SUM(active) >= ?) AND"""
                params.append(int(data[arg]))
            elif arg == "timeframe":
                param = parse(data[arg])
                param_utc = param.astimezone(UTC)
                query += """scheduled_start BETWEEN DATETIME('now')
                            AND DATETIME(?) AND """
                params.append(param_utc)
            elif arg.startswith("name-"):
                query += "name LIKE ? AND "
                param = data[arg]
                if arg == "name-start":
                    param = data[arg] + "%"
                elif arg == "name-end":
                    param = "%" + data[arg]
                elif arg == "name-contains":
                    param = "%" + data[arg] + "%"
                params.append(param)
            else:
                arg = arg.replace("-", "_")
                query += f"{arg} = ? AND "
                params.append(data[arg])
        query = query[:-4]
        print(query, params)
        cur.execute(query, params)

    else:
        cur.execute(query)

    events = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in events]), 200

@app.route("/events/<string:name>", methods=['PUT'])
def update_event(name):

    """
    Updates the event with the given name, setting new values in the
    database for each specified parameter.

    Possible Parameters:
    slug: updates the slug in the database to the specified value in the query
            string
    active: updates the active status in the database to the specified value
            in the query string
    scheduled-start: updates the scheduled start in the database to the 
                    specified value in the query string (in UTC)
    type: updates the type in the database to the specified value in the query
          string
    status: updates the status in the database to the specified value in the
            query string
    
    Name cannot be updated because it is a primary key
    Sport cannot be updated because it is a foreign key referencing the sports table
    """

    data = request.args

    if len(data) == 0:
        return jsonify({'error': 'No data provided to update'}), 400
    
    if 'status' in data.keys() and data['status'].lower() not in \
        ['pending', 'started', 'ended', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    if 'type' in data.keys() and data['type'].lower() not in \
        ['preplay', 'inplay']:
        return jsonify({'error': 'Invalid event type'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    update_fields = []
    update_params = []

    for arg in data:
        if arg == "scheduled-start":
            scheduled_start = parse(scheduled_start)
            scheduled_start_utc = scheduled_start.astimezone(UTC)
            update_params.append(scheduled_start_utc)
        else:
            update_params.append(data[arg])
        update_fields.append(f"{arg} = ?")

    update_params.append(name)

    query = f"UPDATE events SET {', '.join(update_fields)} WHERE name = ?"
    cur.execute(query, update_params)

    if 'status' in data.keys():
        status = data['status']

        # if the status is started,
        # the actual start should be set to the current time,
        # and the event type should be set to Inplay, as play has begun
        if status.lower() == "started":
            cur.execute("UPDATE events SET actual_start = ? WHERE name = ?",
                        (datetime.now(timezone.utc), name))
            cur.execute("UPDATE events SET type = 'Inplay' WHERE name = ?",
                        (name,))

        # if the status is ended or cancelled,
        # the event should be inactive, as it is no longer taking place
        elif status.lower() in ["ended", "cancelled"]:
            cur.execute("UPDATE events SET active = 0 WHERE name = ?", (name,))
            cur.execute("""UPDATE sports SET active = 0 WHERE name IN
                        (SELECT sport FROM events GROUP BY sport 
                        HAVING SUM(active) = 0)""")

    
    if 'active' in data.keys():
        active = data['active']
        
        # for any update that deactivates an event,
        # check if it was the last one for its sport
        if active.lower() in ["false", "0"]:
            cur.execute("""UPDATE sports SET active = 0 WHERE name IN
                        (SELECT sport FROM events GROUP BY sport 
                        HAVING SUM(active) = 0)""")

    conn.commit()
    conn.close()
    return jsonify({'message': 'Updated successfully'}), 200

@app.route("/events/<string:name>", methods=['DELETE'])
def delete_event(name):

    """
    Deletes an event with the given name from the events table
    """

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM events WHERE name = ?", (name,))
    except sqlite3.Error as e:
        return jsonify({'error': f'error deleting event {e}'})
    conn.commit()
    conn.close()
    return jsonify({'message': "event deleted"}), 204

@app.route("/selections", methods=['POST'])
def create_selection():

    """
    Create a new selection with a given name, event, price, 
    and optionally an active status. If an active status is not 
    provided, False will be assumed by default, as the selection is new
    """

    try:
        name = request.args.get('name')
        event = request.args.get('event')
        # convert price to float with 2 decimal places
        price = "{:.2f}".format(float(request.args.get('price')))
        active = request.args.get('active') or False
        
        if type(active) == "str":
            if active.lower() in ["false", "0"]:
                active = False
            elif active.lower() in ["true", "1"]:
                active = True
            else:
                return jsonify({'error': "active must be either true or false"}), 400
            
        # outcome will be Unsettled by default, as we don't know the result yet
        outcome = "Unsettled"

        if not (name and event and price):
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

    """
    Searches the selections table for all records, or when query parameters
    are specified, all records that match those criteria.

    Possible parameters:
    min-price: gets all selections whose price is the given value or more
    max-price: gets all selections whose price is the given value or less
    name-start: gets all selections whose name starts with the given string
    name-end: gets all selections whose name ends with the given string
    name-contains: gets all selections whose name contains the given string
                    anywhere in its name
    name: gets all selections whose name exactly matches the given string
    event: gets all selections whose event matches the given string
    price: gets all selections whose price exactly matches the given value
    active: gets all selections whose active status matches the given string
    outcome: gets all selections whose outcome exactly matches the given
             string
    """
    data = request.args

    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT * FROM selections"

    params = []

    if len(data) != 0:
        query += " WHERE "
        for arg in data:
            # prices must always be shown with two decimal places
            if arg == "min-price":
                query += "price >= ? AND"
                params.append("{:.2f}".format(float(data[arg])))
            elif arg == "max-price":
                query += "price <= ? AND"
                params.append("{:.2f}".format(float(data[arg])))
            elif arg.startswith("name-"):
                query += "name LIKE ? AND "
                param = data[arg]
                if arg == "name-start":
                    param = data[arg] + "%"
                elif arg == "name-end":
                    param = "%" + data[arg]
                elif arg == "name-contains":
                    param = "%" + data[arg] + "%"
                params.append(param)
            else:
                arg = arg.replace("-", "_")
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

    """
    Updates the selection with the given name, setting new values in the
    database for each specified parameter.

    Possible Parameters:
    price: updates the price in the database to the specified value in the query
           string
    active: updates the active status in the database to the specified value
            in the query string
    outcome: updates the outcome in the database to the specified value in the
             query string
    
    Name cannot be updated because it is a primary key
    Event cannot be updated because it is a foreign key referencing the events table
    """

    data = request.args

    if len(data) == 0:
        return jsonify({'message': 'No data provided to update'}), 400
    
    if 'outcome' in data.keys() and data['outcome'].lower() not in \
        ['win', 'lose', 'void', 'unsettled']:
        return jsonify({'error': 'Invalid outcome'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    update_fields = []
    update_params = []

    for arg in data:
        if arg == "price":
            update_params.append("{:.2f}".format(float(data[arg])))
        else:
            update_params.append(data[arg])
        update_fields.append(f"{arg} = ?")

    update_params.append(name)

    query = f"UPDATE selections SET {', '.join(update_fields)} WHERE name = ?"
    cur.execute(query, update_params)

    if "outcome" in data.keys():
        outcome = data['outcome']
        
        # if the outcome is not unsettled, it is either a win, loss or void,
        # all of which mean the selection is inactive
        if outcome.lower() != "unsettled":
            cur.execute("UPDATE selections SET active = 0 WHERE name = ?", 
                        (name,))
            cur.execute("""UPDATE events SET active = 0 WHERE name IN
                        (SELECT event FROM selections GROUP BY event 
                        HAVING SUM(active) = 0)""")
            # if the event was the last event for its sport,
            # the sport should also be inactive
            cur.execute("""UPDATE sports SET active = 0 WHERE name IN
                    (SELECT sport FROM events GROUP BY sport 
                    HAVING SUM(active) = 0)""")
    
    if "active" in data.keys():
        active = data['active']

        # if selection is set to inactive, and it was the last selection
        # for its event, set the event to inactive
        if active.lower() in ["false", "0"]:
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

    """
    Deletes a selection with the given name from the selections table
    """

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM selections WHERE name = ?", (name,))
    except sqlite3.Error as e:
        return jsonify({'error': f'error deleting event {e}'})
    conn.commit()
    conn.close()
    return jsonify({'message': "selection deleted"}), 204

if __name__ == '__main__':
    init_db()
    app.run()
