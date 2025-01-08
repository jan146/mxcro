
SESSION_NAME="mxcro"

# Create new session
tmux new -s "$SESSION_NAME" -x "$(tput cols)" -y "$(tput lines)" -d

# First window: backend
# Open NeoVIM in top pane
tmux send-keys -t "$SESSION_NAME" "nvim ." C-m
# Split horizontally (vertically stacked)
tmux split-window -v -l "33%"
# Run shell with activated venv in lower pane
tmux send-keys -t "$SESSION_NAME" ". venv/bin/activate" C-m
# Run database in bottom-right pane
tmux split-window -h
tmux send-keys -t "$SESSION_NAME" "podman-compose -f compose-mongo.yaml up" C-m
# Let's also run combined API here
tmux split-window -v -l "50%"
tmux send-keys -t "$SESSION_NAME" ". venv/bin/activate && python api.py" C-m

# Run API for all three microservices right of code editor
# tmux select-pane -t "${SESSION_NAME}.0"
# tmux split-window -h -l "25%"
# tmux send-keys -t "$SESSION_NAME" ". venv/bin/activate && python -m food_item.src.api.v1.api" C-m
# tmux split-window -v -l "66%"
# tmux send-keys -t "$SESSION_NAME" ". venv/bin/activate && python -m user_info.src.api.v1.api" C-m
# tmux split-window -v -l "50%"
# tmux send-keys -t "$SESSION_NAME" ". venv/bin/activate && python -m logged_item.src.api.v1.api" C-m
# tmux attach -t "$SESSION_NAME"

# Create new window for frontend
tmux new-window
# Open NeoVIM in top pane
tmux send-keys -t "$SESSION_NAME" "cd mxcro-frontend && nvim ." C-m
# Split horizontally (vertically stacked)
tmux split-window -v -l "33%"
tmux send-keys -t "$SESSION_NAME" "cd mxcro-frontend" C-m
# Run terminal in bottom-left pane and bun in bottom-right pane
tmux split-window -h
tmux send-keys -t "$SESSION_NAME" "cd mxcro-frontend; bun run dev" C-m

# Attach to session
tmux attach -t "$SESSION_NAME"

