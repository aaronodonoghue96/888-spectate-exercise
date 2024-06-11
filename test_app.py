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

import unittest
import requests

class TestCases(unittest.TestCase):

    """
    A test cases class to hold all the unit tests for the CRUD REST API
    """

    def test_create_sport_with_required_params(self):
        
        """
        Tests making a post request to create a new sport with the
        required query parameters (i.e. name), ensuring the correct
        response code and the correct number of entries in the database
        after the new sport has been created
        """
        
        params = {"name": "football"}
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

        params = {"name": "football", "slug": "football", "active": "false"}
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

    def test_search_sports(self):
        # test no params
        # test one param
        # test name regexes
        # test many params
        # test num active events
        # test invalid params
        # test empty search - sport that doesn't exist
        pass

    def test_update_sport(self):
        # test no params
        # test invalid params
        # test invalid type
        # test one param
        # test both params
        pass

    def test_delete_sport(self):
        # test correct
        # test dependent - doesn't delete
        # test invalid - not found
        # test empty
        pass

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
                  "slug": "arsenal-vs-liverpool", "active": "False",
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

    def test_search_events(self):
        # test no params
        # test one param
        # test name regexes
        # test many params
        # test num active selections
        # test invalid params
        # test timezone search - ensure displayed in correct timezones
        # test empty search - event that doesn't exist
        pass

    def test_update_event(self):
        # test no params
        # test invalid params
        # test invalid type
        # test one param
        # test many params
        # test setting of actual start
        # test cascade to change active from status
        # test last active gone = sport inactive
        pass

    def test_delete_event(self):
        # test correct
        # test dependent - doesn't delete
        # test invalid - not found
        # test empty
        pass

    def test_create_selection_with_required_params(self):
        params = {"name": "football", "event": "Man Utd vs Chelsea", "price":"3.00"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_selection_with_all_params(self):
        params = {"name": "football", "event": "Man Utd vs Chelsea", "price":"3.00", "active": "false"}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 201)

    def test_create_selection_empty(self):
        url = "http://127.0.0.1:5000/selections"
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 400)

    def test_create_selection_missing_required_params(self):
        params = {'active': 'False'}
        url = "http://127.0.0.1:5000/selections?"
        for key, value in params.items():
            url += key + "=" + value + " &"
        url = url[:-1] # remove final &
        response = requests.post(url, timeout=60)
        self.assertEqual(response.status_code, 400)

    def test_search_selections(self):
        # test no params
        # test one param
        # test name regexes
        # test many params
        # test max/min price
        # test invalid params
        # test empty search - sport that doesn't exist
        pass

    def test_update_selection(self):
        # test no params
        # test invalid params
        # test invalid type
        # test one param
        # test many params
        # test cascade to change active from outcome
        # test last active gone = event inactive
        pass

    def test_delete_selection(self):
        # test correct
        # test dependent - doesn't delete
        # test invalid - not found
        # test empty
        pass

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
