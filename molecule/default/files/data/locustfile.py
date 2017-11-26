from locust import Locust, TaskSet, task

class MyTaskSet(TaskSet):
    @task
    def my_task(self):
        print("this is my task!")

class MyLocust(Locust):
    task_set = MyTaskSet
    min_wait = 500
    max_wait = 1000
