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
    local script_path="$(dirname "$script_name")"  # Extract directory from script path
    local script_basename="$(basename "$script_name")"  # Extract script basename

    log "Running ${script_name}..."
    (
        cd "$script_path"  # Change directory
        if [[ "$script_basename" == "upload_to_huggingface.py" ]]; then
            if python3 "$script_basename" "$2"; then
                log "${script_name} completed successfully."
            else
                log "Error: ${script_name} failed"
                exit 1
            fi
        else
            if python3 "$script_basename"; then
                log "${script_name} completed successfully."
            else
                log "Error: ${script_name} failed"
                exit 1
            fi
        fi
    )
}

run_scrapy_spider() {
    log "Running Scrapy spider..."
    (
        cd src/landscape_scraper  # Change directory to where the Scrapy project is
        if scrapy crawl files -O output.json; then
            log "Scrapy spider completed successfully."
        else
            log "Error: Scrapy spider failed"
            exit 1
        fi
    )
}

run_etl() {
    log "Starting ETL process..."

    etl_scripts=(
        "src/scripts/landscape_explorer.py"
    )

    for script in "${etl_scripts[@]}"; do
        run_python_script "$script"
    done

    run_scrapy_spider

    etl_scripts_continued=(
        "src/scripts/augment_landscape.py"
        "src/scripts/landscape_extractor.py"
        "src/scripts/Unified_format_conversation.py"
        "src/scripts/upload_to_huggingface.py"
    )

    for script in "${etl_scripts_continued[@]}"; do
        if [[ $script == *"upload_to_huggingface.py" ]]; then
            run_python_script "$script" "$DATA_SET_ID"
        else
            run_python_script "$script"
        fi
    done

    log "ETL process completed."
}

run_qa() {
    log "Starting Q&A generation process..."

    qa_scripts=(
        "src/scripts/qa_generation/qa_generation.py"
        "src/scripts/upload_qa_to_hugging_face.py"
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

# check first if input is valid, check if all arguments are either etl or qa or dataset id
if [ $# -eq 0 ]; then
    log "No arguments provided. Usage: $0 [etl] [qa] <data_set_id>"
    exit 1
fi

# Validate and process arguments
ETL=false
QA=false
DATA_SET_ID=""

for arg in "$@"; do
    case $arg in
        etl)
            ETL=true
            ;;
        qa)
            QA=true
            ;;
        *)
            if [[ -z "$DATA_SET_ID" ]]; then
                DATA_SET_ID="$arg"
            else
                log "Invalid argument: $arg"
                log "Usage: $0 [etl] [qa] <data_set_id>"
                exit 1
            fi
            ;;
    esac
done

if [[ -z "$DATA_SET_ID" ]]; then
    log "Error: Data set ID is required."
    log "Usage: $0 [etl] [qa] <data_set_id>"
    exit 1
fi

log "Data set ID: $DATA_SET_ID"


setup_virtual_environment
load_env

if $ETL; then
    run_etl
fi

if $QA; then
    run_qa
fi

if ! $ETL && ! $QA; then
    log "No ETL or QA specified, running both"
    run_etl
    run_qa
fi

log "All selected tasks ran successfully."
