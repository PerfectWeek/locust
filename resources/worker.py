from locust import HttpLocust, TaskSet, task
import random
import string
import json

def register(l):
    letters = string.ascii_lowercase
    l.username = ''.join(random.choice(letters) for i in range(20))
    l.email = ''.join(random.choice(letters) for i in range(20)) + '@test.com'
    l.password = ''.join(random.choice(letters) for i in range(10)).join(random.choice(string.ascii_uppercase) for i in range(10)).join(random.choice(string.digits) for i in range(10)) + "+-_"
    resp = l.client.post("/auth/local/register", data=json.dumps({"name":l.username, "email": l.email, "password": l.password}), headers={'Content-Type': 'application/json'})
    data = json.loads(resp.text)
    l.client.get("/auth/local/validate-email/" + data.get('uuid'), name="/auth/local/validate-email/:uuid")

def login(l):
    resp = l.client.post("/auth/local/login", data=json.dumps({"email": l.email, "password": l.password}), headers={'Content-Type': 'application/json'})
    data = json.loads(resp.text)
    l.token = data.get('token')

class UserTasks(TaskSet):
    def on_start(self):
        register(self)
        login(self)
        self.calendars = []
        self.events = []

    @task
    def index(self):
        resp = self.client.get("/")
        print('index')
        print(resp.text)

    @task
    def my_profile(self):
        resp = self.client.get("/users/me", headers={'Authorization': 'Bearer ' + self.token})
        print('my_profile')
        print(resp.text)
    
    @task
    def edit_my_username(self):
        letters = string.ascii_lowercase
        self.username = ''.join(random.choice(letters) for i in range(20))
        resp = self.client.put("/users/me", data=json.dumps({"name": self.username, "email": self.email}), headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        print('edit_my_username')
        print(resp.text)
    
    @task
    def create_calendar(self):
        letters = string.ascii_lowercase
        calendar_name = ''.join(random.choice(letters) for i in range(20))
        calendar_color = '#188ae2'
        resp = self.client.post("/calendars", data=json.dumps({"name": calendar_name, "color": calendar_color}), headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        print(resp.text)
        data = json.loads(resp.text)
        self.calendars.append(data.get('calendar').get('id'))
        print('create_calendar')
        print(resp.text)
    
    @task
    def delete_calendar(self):
        if len(self.calendars):
            rand_idx = random.randint(0, len(self.calendars) - 1)
            resp = self.client.delete("/calendars/" + str(self.calendars[rand_idx]), name="/calendars/:calendarId", headers={'Authorization': 'Bearer ' + self.token})
            self.calendars.remove(self.calendars[rand_idx])
            print('delete_calendar')
            print(resp.text)

    @task
    def get_calendars(self):
        self.client.get("/calendars", headers={'Authorization': 'Bearer ' + self.token})

    @task
    def create_event(self):
        letters = string.ascii_lowercase
        event_name = ''.join(random.choice(letters) for i in range(20))
        event_color = '#188ae2'
        event_start = 1234
        event_end = 4321
        event_type = 'hobby'
        event_visibility = 'public'
        event_desc = ''.join(random.choice(letters) for i in range(100))
        event_location = ''.join(random.choice(letters) for i in range(50))
        resp = self.client.post("/events", data=json.dumps({
            "name": event_name,
            "color": event_color,
            "start_time": event_start,
            "end_time": event_end,
            "type": event_type,
            "visibility": event_visibility,
            "description": event_desc,
            "location": event_location
        }), headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        data = json.loads(resp.text)
        self.events.append(data.get('event').get('id'))
        print('create_event')
        print(resp.text)
    
    @task
    def get_events(self):
        resp = self.client.get("/events", headers={'Authorization': 'Bearer ' + self.token})
        print('get_events')
        print(resp.text)

    @task
    def delete_event(self):
        if len(self.events):
            rand_idx = random.randint(0, len(self.events) - 1)
            resp = self.client.delete("/events/" + str(self.events[rand_idx]), name="/events/:eventId", headers={'Authorization': 'Bearer ' + self.token})
            self.events.remove(self.events[rand_idx])
            print('delete_event')
            print(resp.text)



# remove event

class WebsiteUser(HttpLocust):
    task_set = UserTasks
