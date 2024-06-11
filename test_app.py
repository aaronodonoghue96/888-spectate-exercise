"""
Unit tests for the CRUD REST API, covering create, read, update and delete
functionality for all three tables.

Create tests include:
Testing with the correct parameters
Testing with all parameters, including those that have a default value
Testing with no parameters
Testing with missing parameters

Read tests include:
Testing with no parameters (i.e. find all)
Testing with one parameter
Testing with many parameters
Testing with invalid parameters
Testing with a search that returns no results
Testing the name regexes match correctly
Testing the min-events/min-selections parameters work correctly
Testing the min-price/max-price parameters for selections work correctly

Update tests include:
Testing with no parameters
Testing with an invalid parameter
Testing with an invalid value (e.g. trying to pass a string for price)
Testing with one parameter
Testing with many parameters
Testing that setting an event's status to Started will set the actual start
and set its type to Inplay
Testing that updating an event's status to Ended or Cancelled will set
it to inactive

Delete tests include:
Testing with an existing record
Testing with a dependent record (won't delete as there are entries in
another table referring to it)
Testing with an invalid record (there's nothing to delete, as that value
isn't in the database)
Testing with an empty value
"""

import sqlite3
import unittest
import requests
import app

class TestCases(unittest.TestCase):

    """
    A test cases class to hold all the unit tests for the CRUD REST API
    """

    def test_create_sport_with_required_params(self):#
    
        """
        Tests making a post request to create a new sport with the
        required query parameters (i.e. name), ensuring the correct
        response code and the correct number of entries in the database
        after the new sport has been created
        """

        params = {"name": "golf"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_sport_with_all_params(self):

        """
        Tests making a post request to create a new sport with all
        query parameters (i.e. name, slug, active), ensuring the correct
        response code and the correct number of entries in the database
        after the new sport has been created
        """

        params = {"name": "football", "slug": "football", "active": "1"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_sport_empty(self):
        url = "http://127.0.0.1:5000/sports"
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 400)

    def test_create_sport_missing_required_params(self):
        params = {'active': 'False'}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + " &"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 400)

    def test_search_sports_no_params(self):
        url = "http://127.0.0.1:5000/sports"
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        
    def test_search_sports_one_param(self):
        params = {"name": "football"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertEqual(entry["name"], "football")

    def test_search_sports_name_match(self):
        params = {"name-start": "foot"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertTrue(entry["name"].startswith("foot"))

    def test_search_sports_multiple_params(self):
        params = {"name": "football", "slug": "football", "active": "0"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertEqual(entry["name"], "football")
            self.assertEqual(entry["slug"], "football")
            self.assertEqual(entry["active"], "0")

    def test_search_sports_min_events(self):
        params = {"min-events": "1"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        self.assertEqual(len(json_entries), 1)
     
    def test_search_sports_invalid_param(self):
        params = {"invalid": "test"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 404)
 
    def test_search_sports_no_match(self):
        params = {"name": "nonexistent"} # there's no entry for this in sports
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    def test_update_sport_no_params(self):
        url = "http://127.0.0.1:5000/sports/football"
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 400)
  
    def test_update_sport_one_param(self):
        params = {'slug': 'soccer'}
        url = "http://127.0.0.1:5000/sports/football"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 200)

    def test_update_sport_multiple_params(self):
        params = {'name': 'Football', 'active': '1'}
        url = "http://127.0.0.1:5000/sports/football"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 200)

    def test_update_sport_invalid_params(self):
        params = {'test': 'nonexistent'}
        url = "http://127.0.0.1:5000/sports/football"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 500)

    def test_update_sport_one_param(self):
        pass

    def test_update_sport_multiple_params(self):
        pass

    def test_update_sport_invalid_params(self):
        pass

    def test_delete_sport_existing(self):
        url = "http://127.0.0.1:5000/events/golf"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 204)

    def test_delete_sport_nonexistent(self):
        url = "http://127.0.0.1:5000/sports/doesnt-exist"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 204)

    def test_delete_sport_empty(self):
        url = "http://127.0.0.1:5000/sports/"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 404)

    def test_create_event_with_required_params(self):
        params = {"name": "Man Utd vs Chelsea", "sport": "football",
                  "scheduled-start": "2024-06-16 15:00:00 +00:00"}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_event_with_all_params(self):
        params = {"name": "Arsenal vs Liverpool", "sport": "football",
                  "slug": "arsenal-vs-liverpool", "active": "1",
                  "scheduled-start": "2024-06-17 15:00:00 +00:00"}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_event_empty(self):
        url = "http://127.0.0.1:5000/events"
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 400)

    def test_create_event_missing_required_params(self):
        params = {'active': 'False'}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + " &"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 400)
    
    def test_search_events_no_params(self):
        url = "http://127.0.0.1:5000/events"
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        
    def test_search_events_one_param(self):
        params = {"name": "Man Utd vs Chelsea"}
        url = "http://127.0.0.1:5000/sports?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertEqual(entry["name"], "Man Utd vs Chelsea")

    def test_search_events_name_match(self):
        params = {"name-end": "Chelsea"}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertTrue(entry["name"].endswith("Chelsea"))

    def test_search_events_multiple_params(self):
        params = {"name": "Man Utd vs Chelsea", "slug": "man-utd-vs-chelsea", "status": "Pending"}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertEqual(entry["name"], "Man Utd vs Chelsea")
            self.assertEqual(entry["slug"], "man-utd-vs-chelsea")
            self.assertEqual(entry["status"], "Pending")

    def test_search_events_min_selections(self):
        params = {"min-selections": "1"}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        self.assertEqual(len(json_entries), 1)

    def test_search_events_timeframe(self):
        params = {"timeframe": "2024-06-17 18:00:00 +02:00"}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        self.assertEqual(len(json_entries), 2)
     
    def test_search_events_invalid_param(self):
        params = {"invalid": "test"}
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 500)
 
    def test_search_events_no_match(self):
        params = {"name": "nonexistent"} # there's no entry for this in events
        url = "http://127.0.0.1:5000/events?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)
        
    def test_search_selections_no_params(self):
        url = "http://127.0.0.1:5000/selections"
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
    
    def test_search_selections_one_param(self):
        params = {"name": "Man U"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertEqual(entry["name"], "Man U")

    def test_search_selections_name_match(self):
        params = {"name-contains": "Man"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertTrue("Man" in entry["name"])

    def test_search_selections_multiple_params(self):
        params = {"name": "Man Utd vs Chelsea", "price": "3.00"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        for entry in json_entries:
            self.assertEqual(entry["name"], "Man Utd vs Chelsea")
            self.assertEqual(entry["price"], "3.00")

    def test_search_selections_min_price(self):
        params = {"min-price": "2.00"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        self.assertEqual(len(json_entries), 2)
 
    def test_search_selections_max_price(self):
        params = {"max-price": "4.00"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        json_entries = response.json()
        self.assertEqual(len(json_entries), 2)
     
    def test_search_selections_invalid_param(self):
        params = {"invalid": "test"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 500)
 
    def test_search_selections_no_match(self):
        params = {"name": "nonexistent"} # there's no entry for this in events
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.get(url, timeout=60)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)
    
    def test_update_event_no_params(self):
        url = """http://127.0.0.1:5000/events/Man Utd vs Chelsea"""
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 400)

    def test_update_event_one_param(self):
        params = {'slug': 'manchester-v-chelsea'}
        url = """http://127.0.0.1:5000/events/Man Utd vs Chelsea?"""
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 200)

    def test_update_event_multiple_params(self):
        params = {'slug': 'utd-v-chelsea', 'active': '1'}
        url = """http://127.0.0.1:5000/events/Man Utd vs Chelsea?"""
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 200)

    def test_update_event_invalid_params(self):
        params = {'price': 'nonexistent'}
        url = """http://127.0.0.1:5000/events/Man Utd vs Chelsea?"""
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 500)

    def test_delete_event_existing(self):
        url = """http://127.0.0.1:5000/events/Arsenal vs Liverpool"""
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 204)

    def test_delete_event_nonexistent(self):
        url = "http://127.0.0.1:5000/events/doesnt-exist"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 204)
 
    def test_delete_event_empty(self):
        url = "http://127.0.0.1:5000/events/"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 404)

    def test_create_selection_with_required_params(self):
        params = {"name": "Man Utd", "event": "Man Utd vs Chelsea", "price":"3.00"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_selection_with_all_params(self):
        params = {"name": "Chelsea", "event": "Man Utd vs Chelsea", "price":"3.00",
                  "active": "1"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_selection_empty(self):
        url = "http://127.0.0.1:5000/selections"
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 500)

    def test_create_selection_missing_required_params(self):
        params = {'active': '1'}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + " &"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 500)

    def test_update_selection_no_params(self):
        url = "http://127.0.0.1:5000/selections/Chelsea"
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 400)
        
    def test_update_selection_one_param(self):
        params = {'price': '3.50'}
        url = "http://127.0.0.1:5000/selections/Chelsea?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 200)

    def test_update_selection_multiple_params(self):
        params = {'price': '4.50', 'active': '1'}
        url = "http://127.0.0.1:5000/selections/Chelsea?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 200)

    def test_update_selection_invalid_params(self):
        params = {'test': 'nonexistent'}
        url = "http://127.0.0.1:5000/selections/Chelsea?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.put(url, timeout=60)
        self.assertEqual(response.status_code, 500)

    def test_delete_selection_existing(self):
        url = "http://127.0.0.1:5000/selections/test"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 204)

    def test_delete_selection_nonexistent(self):
        url = "http://127.0.0.1:5000/selections/doesnt-exist"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 204)

    def test_delete_selection_empty(self):
        url = "http://127.0.0.1:5000/events/"
        response = requests.delete(url, timeout=60)
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    DATABASE = "app.db"
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON") # ensure foreign keys are enabled
    cursor = conn.cursor()
    
    # make sure to drop tables and recreate them so tests will be consistent
    cursor.execute("DROP TABLE IF EXISTS selections")
    cursor.execute("DROP TABLE IF EXISTS events")
    cursor.execute("DROP TABLE IF EXISTS sports")
    
    app.init_db()

    tests = TestCases()
    tests.test_create_sport_with_required_params()
    tests.test_create_sport_with_all_params()
    tests.test_create_sport_empty()
    tests.test_create_sport_missing_required_params()
    tests.test_create_event_with_required_params()
    tests.test_create_event_with_all_params()
    tests.test_create_event_empty()
    tests.test_create_event_missing_required_params()
    tests.test_create_selection_with_required_params()
    tests.test_create_selection_with_all_params()
    tests.test_create_selection_empty()
    tests.test_create_selection_missing_required_params()
    tests.test_search_sports_no_params()
    tests.test_search_sports_one_param()
    tests.test_search_sports_min_events()
    tests.test_search_sports_multiple_params()
    tests.test_search_sports_name_match()
    tests.test_search_sports_no_match()
    tests.test_search_events_no_params()
    tests.test_search_events_one_param()
    tests.test_search_events_timeframe()
    tests.test_search_events_multiple_params()
    tests.test_search_events_min_selections()
    tests.test_search_events_invalid_param()
    tests.test_search_events_name_match()
    tests.test_search_selections_no_match()
    tests.test_search_selections_no_params()
    tests.test_search_selections_one_param()
    tests.test_search_selections_multiple_params()
    tests.test_search_selections_min_price()
    tests.test_search_selections_max_price()
    tests.test_search_selections_invalid_param()
    tests.test_search_selections_name_match()
    tests.test_search_selections_no_match()
    tests.test_update_sport_no_params()
    tests.test_update_sport_one_param()
    tests.test_update_sport_multiple_params()
    tests.test_update_sport_invalid_params()
    tests.test_update_event_no_params()
    tests.test_update_event_one_param()
    tests.test_update_event_multiple_params()
    tests.test_update_event_invalid_params()
    tests.test_update_selection_no_params()
    tests.test_update_selection_one_param()
    tests.test_update_selection_multiple_params()
    tests.test_update_selection_invalid_params()
    tests.test_delete_sport_existing()
    tests.test_delete_sport_nonexistent()
    tests.test_delete_sport_empty()
    tests.test_delete_event_existing()
    tests.test_delete_event_nonexistent()
    tests.test_delete_event_empty()
    tests.test_delete_selection_existing()
    tests.test_delete_selection_nonexistent()
    tests.test_delete_selection_empty()