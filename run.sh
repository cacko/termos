#!/bin/zsh

direnv exec . mamba run --live-stream -vvvv --dev -n termo-service uvicorn 'termo_service.app:create_app' --host 192.168.0.107 --port 23727 --workers 1  --log-level info --use-colors --factory --loop uvloop --access-log
