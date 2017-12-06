from locust import Locust, TaskSet, task, events

# Dummy locustfile.
#
# This does not actually perform any requests, but pretends to,
# so that we do not need a "target" host.

class MyTaskSet(TaskSet):
    @task
    def my_task(self):
        events.request_success.fire(
            request_type="GET",
            name="/",
            response_time=421,
            response_length=1234)

class MyLocust(Locust):
    task_set = MyTaskSet
    min_wait = 500
    max_wait = 1000

