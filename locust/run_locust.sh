#!/bin/bash

locust -f /mnt/locust/locustfile.py --headless -u 100 -r 10 --run-time 1m --host http://nginx:80 --html /mnt/locust/report.html