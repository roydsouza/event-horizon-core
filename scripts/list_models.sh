#!/bin/bash

# Check if ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Ollama is not running."
    echo "Starting Ollama server..."
    # Attempt to start via brew services if available, else background process
    if brew services list | grep ollama > /dev/null; then
         brew services start ollama
         echo "Waiting for service to start..."
         sleep 5
    else
         echo "Please start ollama manually: 'ollama serve'"
         exit 1
    fi
fi

echo "Listing installed models..."
ollama list
