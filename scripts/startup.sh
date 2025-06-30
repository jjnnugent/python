#!/usr/bin/bash
tmux new-session -ds logs
tmux split-window -t logs
tmux split-window -t logs
tmux split-window -t logs
# tmux send-keys -t logs.0 "python3 ~/python/slack/tftbot/main.py" ENTER
tmux send-keys -t logs.0 "echo tftbot down until further notice" ENTER
tmux send-keys -t logs.1 "git -C ~/python/ fetch && git -C ~/python/ reset --hard origin/main && uv run --directory ~/python/slack/watcher/ ~/python/slack/watcher/main.py" ENTER
tmux send-keys -t logs.2 "git -C ~/python/ fetch && git -C ~/python/ reset --hard origin/main && uv run --directory ~/python/slack/meeseeks/ ~/python/slack/meeseeks/main.py" ENTER
tmux send-keys -t logs.3 "tail -f ~/logs/ash_nazg.log | grep -ve \"\[DEBUG\]\"" ENTER
tmux select-pane -T tftbot -t logs.0
tmux select-pane -T watcher -t logs.1
tmux select-pane -T mrmeeseeks -t logs.2
tmux select-pane -T watchlist -t logs.3
tmux select-layout -t logs even-vertical
