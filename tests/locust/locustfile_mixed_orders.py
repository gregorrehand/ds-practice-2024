import random

from locust import HttpUser, TaskSet, task, between


class BuyTaskSet(TaskSet):
    @task
    def buy(self):
        payload = {
                "user": {
                    "name": ("Peeter" if random.random() < 0.5 else "peeter"),
                    "contact": "Peeter.pets@gmail.com",
                },
                "creditCard": {
                    "number": "4381294673",
                    "expirationDate": ("09/25" if random.random() < 0.5 else "09/23"),
                    "cvv": "423",
                },
                "userComment": "",
                "items": [
                    {
                        "name": "JavaScript - The Good Parts",
                        "quantity": 1,
                    },
                ],
                "discountCode": "",
                "shippingMethod": "",
                "giftMessage": "",
                "billingAddress": {
                    "street": "Street1",
                    "city": "Tartu",
                    "state": "Tartu",
                    "zip": "13521",
                    "country": "Estonia",
                },
                "giftWrapping": False,
                "termsAndConditionsAccepted": True,
                "notificationPreferences": ['email'],
                "device": {
                    "type": 'Smartphone',
                    "model": 'Samsung Galaxy S10',
                    "os": 'Android 10.0.0',
                },
                "browser": {
                    "name": 'Chrome',
                    "version": '85.0.4183.127',
                },
                "appVersion": '3.0.0',
                "screenResolution": '1440x3040',
                "referrer": 'https://www.google.com',
                "deviceLanguage": 'en-US',
            }

        self.client.post("/checkout", json=payload)


class WebsiteUser(HttpUser):
    tasks = [BuyTaskSet]
    wait_time = between(1, 1)  # Simulates a user waiting between 1 and 5 seconds between tasks
