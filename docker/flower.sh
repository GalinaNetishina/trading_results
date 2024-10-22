#!/bin/bash

cd trading_result_app

celery --app=tasks:celery flower  
