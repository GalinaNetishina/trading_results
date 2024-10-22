#!/bin/bash

cd trading_result_app

celery --app=tasks:celery worker -l INFO --concurrency 2
