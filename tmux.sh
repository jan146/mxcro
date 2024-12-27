
SESSION_NAME="mxcro"

# Create new session
tmux new -s "$SESSION_NAME" -x "$(tput cols)" -y "$(tput lines)" -d
# Open NeoVIM
tmux send-keys -t "$SESSION_NAME" "nvim ." C-m
# Split horizontally (vertically stacked)
tmux split-window -v -l "33%"
# Run shell with activated venv in lower pane
tmux send-keys -t "$SESSION_NAME" ". venv/bin/activate" C-m
# Run database in bottom-right pane
tmux split-window -h
tmux send-keys -t "$SESSION_NAME" "podman-compose -f compose.yaml up" C-m
# Attach to session
tmux attach -t "$SESSION_NAME"

