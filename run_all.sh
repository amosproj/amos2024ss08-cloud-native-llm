#!/bin/bash

# Exit on error, treat unset variables as an error, and make pipeline errors propagate
set -euo pipefail

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Load environment variables from a file
load_env() {
    if [ -f ".env" ]; then
        log "Loading environment variables from .env file..."
        export $(grep -v '^#' .env | xargs -d '\n')
        log "Environment variables loaded."
    else
        log "No .env file found. Make sure to create one with the required environment variables."
        exit 1
    fi
}

# Create and activate Python virtual environment
setup_virtual_environment() {
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
        log "Virtual environment created."
    else
        log "Virtual environment already exists."
    fi

    log "Activating virtual environment..."
    source venv/bin/activate

    log "Installing required packages from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
    log "Required packages installed."
}

run_python_script() {
    local script_name=$1
    log "Running ${script_name}..."
    if python3 "$script_name"; then
        log "${script_name} completed successfully."
    else
        log "Error: ${script_name} failed"
        exit 1
    fi
}

run_etl() {
    log "Starting ETL process..."

    etl_scripts=(
        "src/scripts/landscape_explorer.py"
        "src/scripts/landscape_extractor.py"
        "src/scripts/Unified_format_conversation.py"
        "src/scripts/upload_to_huggingface.py"
    )

    for script in "${etl_scripts[@]}"; do
        run_python_script "$script"
    done

    log "ETL process completed."
}

run_qa() {
    log "Starting Q&A generation process..."

    qa_scripts=(
        "QA_enricher.py"
        "generatefiles.sh"
    )

    for script in "${qa_scripts[@]}"; do
        if [[ $script == *.py ]]; then
            run_python_script "$script"
        else
            log "Running ${script}..."
            if bash "$script"; then
                log "${script} completed successfully."
            else
                log "Error: ${script} failed"
                exit 1
            fi
        fi
    done

    log "Q&A generation process completed."
}

#setup_virtual_environment
load_env

# Parse command-line arguments and run the selected tasks
if [ $# -eq 0 ]; then
    log "No arguments provided. Running both ETL and Q&A generation."
    run_etl
    run_qa
else
    for arg in "$@"; do
        case $arg in
            etl)
                run_etl
                ;;
            qa)
                run_qa
                ;;
            *)
                log "Invalid argument: $arg"
                log "Usage: $0 [etl] [qa]"
                exit 1
                ;;
        esac
    done
fi

log "All selected tasks ran successfully."
