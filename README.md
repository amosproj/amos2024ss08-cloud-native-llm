<div align="center">
  <img src="Deliverables/sprint-01/team-logo.svg" height="256" />
  <p>Open-source LLM for simplifying and understanding the CNCF ecosystem.</p>
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Kubernetes Version](https://img.shields.io/badge/kubernetes-v1.21-blue.svg)
![GitHub language count](https://img.shields.io/github/languages/count/amosproj/amos2024ss08-cloud-native-llm)
![GitHub last commit](https://img.shields.io/github/last-commit/amosproj/amos2024ss08-cloud-native-llm)
![GitHub issues](https://img.shields.io/github/issues/amosproj/amos2024ss08-cloud-native-llm)

## 📖 About 

Deep Cloud Native Computing Foundation, or DeepCNCF for short, is an open-source LLM aimed to simplify the Cloud Native ecosystem by resolving information overload and fragmentation within the CNCF landscape. The aim is to effortlessly provide users with detailed, context-related answers to any CNCF project.

It was developed as part of the [AMOS project](https://github.com/amosproj). Our industry partner is [Kubermatic](https://github.com/kubermatic). The project consists of a pipeline to gather necessary information (including documentation, pdfs, yaml files, jsons, readmes,  and corresponding StackOverflow question/answer pairs) about [CNCF Landscape](https://landscape.cncf.io/) projects, create a question/answer pair dataset from the collected data using [Google Gemma](https://huggingface.co/google/gemma-2b-it), merge it with gathered StackOverflow question/answer pairs, and finetune the [Google Gemma 2B IT model](https://huggingface.co/google/gemma-2b-it), [Google Gemma 7B IT model](https://huggingface.co/google/gemma-7b-it), and [Google Gemma-2 9B IT](https://huggingface.co/google/gemma-2-9b-it) using the gathered data.

## 🚀 Features
- Full data gathering and processing pipeline

  - **[src/landscape_scraper](src/landscape_scraper)**

  - **[src/scripts/scraping](src/scripts/scraping)**

  - **[src/scripts/data_preparation](src/scripts/data_preparation)**

  - **[src/scripts/qa_generation](src/scripts/qa_generation)**

- Training pipeline in 

  - **[src/scripts/training](src/scripts/training)**

  - **[src/hpc_scripts](src/hpc_scripts)**

  - **[src/hpc_scripts/training](src/hpc_scripts/training)**

## 📊 Datasets

- **[cncf-raw-data-for-llm-training](https://huggingface.co/datasets/Kubermatic/cncf-raw-data-for-llm-training)**: raw scraped pdf, readme, json, documentation and yaml data
- **[cncf-question-and-answer-dataset-for-llm-training](https://huggingface.co/datasets/Kubermatic/cncf-question-and-answer-dataset-for-llm-training)**: artifical question/answer pair dataset generated from the raw data using [Google Gemma](https://huggingface.co/google/gemma-2b-it)
- **[stackoverflow_QAs](https://huggingface.co/datasets/Kubermatic/stackoverflow_QAs)**: real question/answer pair dataset gathered from StackOverflow. Only a subset of the questions with the highest rated numbers are included.
- **[Merged_QAs](https://huggingface.co/datasets/Kubermatic/Merged_QAs)**: merged artifical and real question/answer pair dataset
- **[Benchmark-Questions](https://huggingface.co/datasets/Kubermatic/Benchmark-Questions)**: multiple choice question/answer pair dataset used to benchmark the finetuned model.

## 🤖 Models

- **[DeepCNCF](https://huggingface.co/Kubermatic/DeepCNCF)**: initial model trained on [Google Gemma 2B IT model](https://huggingface.co/google/gemma-2b-it)
- **[DeepCNCFQuantized](https://huggingface.co/Kubermatic/DeepCNCFQuantized)**: quantized version of [DeepCNCF](https://huggingface.co/Kubermatic/DeepCNCF/tree/main)
- **[DeepCNCF2BAdapter](https://huggingface.co/Kubermatic/DeepCNCF2BAdapter)**: finetuned [Google Gemma 2B IT model](https://huggingface.co/google/gemma-2b-it), trained on whole dataset
- **[DeepCNCF7BAdapter](https://huggingface.co/Kubermatic/DeepCNCF7BAdapter)**: finetuned [Google Gemma 7B IT model](https://huggingface.co/google/gemma-7b-it), trained on whole dataset
- **[DeepCNCF9BAdapter](https://huggingface.co/Kubermatic/DeepCNCF9BAdapter)**: finetuned [Google Gemma-2 9B IT model](https://huggingface.co/google/gemma-2-9b-it), trained on whole dataset

## 📁 Folder Structure

- **[Deliverables](Deliverables)** Contains all AMOS specific homeworks referenced with the sprint number they were due to.
- **[Documentation](Documentation)** Contains the documentation on how to run the project
- **[src](src)** Contains all the sourcecode of the project.
  - **[src/hpc_scripts](src/hpc_scripts)** Contains sricpts that were specifically tailored to run on the HPC ([High Performance Cluster](https://hpc.fau.de/)) of the FAU. This is mostly for interacting with LLM's
  - **[src/scripts](src/scripts)** Contains all general purpose scripts (i.e. scraping data from CNCF Landscape and Stackoverflow, data formatting, deploying the model)
  - **[src/landscape_scraper](src/landscape_scraper)** Contains scripts for scraping the webpages of the CNCF landscape.
- **[test](test)** Contains all unit tests and integration tests.

## 🤔 Getting Started

If you want to run the data gathering and training pipelines yourself or if you want to use them to gather your own data, follow the steps provided in the **[Documentation](Documentation)**

Additional information can be found in the **[Wiki](../../wiki)**
