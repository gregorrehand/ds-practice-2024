# Tests

First, run the application and go into the test directory
```
sudo docker-compose up --build

cd tests
```

## End-to-end tests
3 automated end-to-end tests simulated with the web gui. 
Each test starts with the homepage and ends with submitting the order.
- 2 tests expect "Transaction Rejected", due to either name or creditcard constraints.
- One test must get "Order Accepted"


### Install cypress
```
npm install cypress --save-dev
```

Run tests:
```
npx cypress run
```

Or run tests with gui:
```
npx cypress open
```

## Concurrency tests
3 tests:
- 4 users buying the same book at the same exact time
- 2 users buying different books at the same exact time
- 5 users are buying the same book at the same time for 20 seconds, with:
  - Fraudulent name 50% of the time
  - Fraudulent credit card 50% of the time


### Install locust
```
pip install locust
```

Run tests:

```
locust -f locust/locustfile_conflicting_orders.py --headless --users 4 --spawn-rate 4 --host 'http://localhost:8081' --run-time 1s --stop-timeout 30s

locust -f locust/locustfile_nonconflicting_orders.py --headless --users 1 --spawn-rate 1 --host 'http://localhost:8081' --run-time 1s --stop-timeout 30s

locust -f locust/locustfile_mixed_orders.py --headless --users 5 --spawn-rate 5 --host 'http://localhost:8081' --run-time 20s --stop-timeout 30s
```
