# 888-spectate-exercise
888 Spectate Coding Exercises (Find Internal Nodes and Python CRUD REST API)

# Find Internal Nodes
Finds the number of internal nodes for a given tree when presented in the form of a list of each node's parent (with -1 for the root, as it has no parent). Runs in O(n) time with O(n) space complexity.

# CRUD REST API (app.py)

A CRUD REST API for managing sports, events and selections, allowing the user to create new entries, search for existing entries that meet one or more criteria using query parameters, update existing entries, and delete existing entries

Technologies Used:
Python
Flask
SQLite 3

## Libraries Used:
unittest (for testing)
requests (for sending requests when testing)
slugify (for making slugs)
datetime (for parsing times)
dateutil (for timezone conversions)

## Design Decisions
* All times are stored in the database as UTC to ensure consistency.
* When the user requests events that will happen in a certain timeframe, the results they will see on-screen will be displayed in UTC time. This can be done only for events, and using the "timeframe" parameter
* All SQL queries were made using raw SQL, no ORMs were used in the making of this API, as per the requirements.
* Cascading updates and deletes are NOT allowed, to ensure no user can accidentally change or remove large numbers of records with as little as one wrong request or parameter. Users cannot update the name of any event, sport or selection, as the name is the primary key, nor can they update what sport an event references, nor what event a selection references, as those are foreign keys.
* Searching using "name" will only find records that match the exact string entered in the query. To allow for partial matching, the parameters "name-start", "name-end" and "name-contains" are available for sports, events and selections, to find records whose name starts with, ends with, or contains the given string respectively.
* Updating the status of an event or selection will check to see if there are any active events/selections remaining for the sport/event in question, and if there are none, it will update the sport/event to inactive, as per the requirements.
* Users can also search for sports/events with a number of active events/selections above a specified value respectively, using the min-events (for sports) and min-selections (for events) parameters.
* Selections also has the option to search for any selections with a minimum or maximum price, returning all selections whose price is greater than or equal to, or less than or equal to the specified value respectively, using the min-price and max-price parameters.
* Slug and active are optional in all cases, and default values will be provided if the user does not specify them (using slugify to make a slug from the name, and using False for active, as a new sport or event will have no events/selections yet)
* Outcome, type and status are all assigned default value, those being Unsettled, Preplay and Pending respectively. This is because the events have not begun yet when they have just been made, so betting will be preplay, the event hasn't started yet, and we don't know the outcome yet. Actual_start is assigned Null when a new event is made, because its value is only determined when the event is set to Started.
* Updating the status of an event to Started will set the actual_start time in the database for the event to the current time, as per the requirements, and will change the type of the event from Preplay to Inplay, as the event has begun.
* Updating the status of an event to Ended or Cancelled will set its 'active' status to False, as the event has finished, so it is no longer active, and since this sets an event to inactive, it will also check if there are any active events left, and if not, set the sport to inactive.
* Updating the outcome of an event to Win, Lose or Void will set the 'active' status to False, as the outcome is known, so it is no longer active, and since this sets an event to inactive, it will also check if there are any active events left, and if not, set the sport to inactive.


## Features

### Intro
* If the user does not add anything to the end of the URL, they will be given a message with instructions on how to use the API to access sports, events or selections

### Create
* Users can create a sport, event or selection using a GET request, using "/sports", "/events" or "/selections" followed by the query string with the required parameters 
  * For sports: name, and optionally slug and active
  * For events: name, type and sport, and optionally slug and active
  * For selections: name, event, price, and optionally active

### Read
* Users can retrieve information on sports, events or selection using a POST request, using "/sports", "/events" or "/selections" optionally followed by the query string with one or more parameters
  * With no query string, it will return all sports/events/selections
  * Parameters for sports are: name, slug, active, min-events, name-start, name-end, name-contains
  * Parameters for events are: name, type, sport, slug, active, type, status, scheduled-start, actual-start, min-selections, name-start, name-end, name-contains, timeframe
  * Parameters for selections are: name, event, price, active, outcome, min-price, max-price, name-start, name-end, name-contains

### Update
* Users can update one or more values for a sport, event or selection using a PUT request, using "/sports/", "/events/" or "/selections/" followed by the name of the sport/event/selection they want to update, and then the query string with one or more parameters for each area they want to update. 
  * NOTE: Name cannot be updated on sports or events when there are dependents referencing them in the events and selections tables respectively. Name can be updated for selections because the name there is not linked to any other table, and names for sports or events with no linked records in other tables can be updated.
  * Parameters for sports are: name, slug, active
  * Parameters for events are: name, type, sport, slug, active, type, status, scheduled-start, actual-start
  * Parameters for selections are: name, event, price, active, outcome
  * As per the Design Decisions section above, updating 'outcome' on a selection to 'Win', 'Lose' or 'Void', or 'status' on an event to 'Ended' or 'Cancelled' can change the active status, updating 'status' on an event to 'Started' will set the actual_start value to the current time, and set the 'type' to Inplay, and updating a selection or event to inactive will check if the event/sport it references has any active selections/sports left, and if not, the event/sport will become inactive too.

### Delete
* Users can delete a sport, event or selection using a DELETE request, using "/sports/", "/events/" or "/selections/" followed by the name of the sport/event/selection they want to delete. No query string is used here.
  * NOTE: Only records with no dependents can be deleted, i.e. any selection can be deleted, but sports and events can only be deleted when they have no events/selections referencing them.

## Testing

Unit testing was performed using the unittest library, and all tests for the CRUD REST API are found in test_app.py. I have also manually tested requests for this assignment using Postman. I have tested a wide range of scenarios, including required inputs, full inputs including optional parameters, empty inputs, invalid parameters, parameters like name matching, min/max price, min events/selections, entering scheduled times in different timezones, and attempting to update/delete an entry with dependents in another table through both unit tests and my own manual testing

Unit tests:
* Create: all passing
* Read: all passing
* Update: all passing
* Delete: all passing

I have also verified via manual testing that the cascade effects (e.g. setting start time when event is updated to Started, setting a sport to inactive when all its events are inactive) work as expected.

I have also performed manual testing for the Find Internal Nodes task to ensure it displays the correct output, including ensuring an empty tree will produce an output of 0, and a tree with just a root will produce an output of 0, ensuring results for worst-case scenarios like a big tree and a straight-line tree (i.e. every node is the child of exactly one other node, forming a straight vertical line) will be calculated correctly