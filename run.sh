#!/bin/zsh
# source ~/.zshrc

direnv exec . mamba run --live-stream -n termo-service python -m termo_service
