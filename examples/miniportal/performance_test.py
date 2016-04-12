from locust import HttpLocust, TaskSet
def index(l):
    l.client.get("/")

def addUser(l):
    l.client.get("/system/usermanager/addUser")

def editUser(l):
    l.client.get("/system/usermanager/editUser")


class UserBehavior(TaskSet):
    tasks = {index: 1, addUser: 2, editUser: 3}


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
