<h1 align="center">
  <img src="/Deliverables/sprint-01/team-logo.png" alt="ChatCNCF team-logo" height="500"/>
</h1>

# Cloud Native LLM Project (AMOS SS 2024)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Kubernetes Version](https://img.shields.io/badge/kubernetes-v1.21-blue.svg)
![GitHub language count](https://img.shields.io/github/languages/count/amosproj/amos2024ss08-cloud-native-llm)
![GitHub last commit](https://img.shields.io/github/last-commit/amosproj/amos2024ss08-cloud-native-llm)
![GitHub issues](https://img.shields.io/github/issues/amosproj/amos2024ss08-cloud-native-llm)


## AMOS Project
This project is a student project for the [AMOS SS 2024](https://github.com/amosproj) course with the industry partner [Kubermatic](https://www.kubermatic.com)
at [Technical University of Berlin](https://www.tu.berlin),[Friedrich-Alexander University of Erlangen-Nuremberg](https://www.fau.de) and [Free University of Berlin](https://www.fu-berlin.de), under the supervision of [Prof. Riehle](https://oss.cs.fau.de/person/riehle-dirk/) and contact persons are Mario Fahlandt and Sebastian Scheele of Kubermatic.

## Overview

Welcome to the Cloud Native LLM Project for the AMOS SS 2024! 

This project aims to simplify the Cloud Native ecosystem by resolving information overload and fragmentation within the CNCF landscape.

Our vision is a future where developers and users can effortlessly obtain detailed, context-aware answers about CNCF projects, thereby boosting productivity and enhancing comprehension.

The development of this project follows an open-source and open-model fashion.

The folder structure is as follows:

- **Deliverables** 1. Contains all AMOS specific homeworks referenced with the sprint number they were due to.
- **Documentation** 2. Contains the documentation on how to run the project
- **src** 3. Contains all the sourcecode of the project.
  - **hpc_scripts** 1. Contains sricpts that were specifically tailored to run on the HPC ([High Performance Cluster](https://hpc.fau.de/)) of the FAU. This is mostly for interacting with LLM's
  - **scripts** 2. Contains all general purpose scripts (i.e. scraping data from CNCF Landscape and Stackoverflow, data formatting, deploying the model)
  - **landscape_scripts** 3. Contains scripts for scraping the webpages of the CNCF landscape.
- **test:** 4. Contains all unit tests and integration tests.

## Objectives

- **Select and Train an Open Source LLM:** Identify a suitable open source LLM for training with specific Kubernetes-related data.
- **Automate Data Extraction:** Develop tools to automatically gather training data from publicly available [Kubernetes resources](https://www.kubermatic.com/company/community/) such as white papers, documentation, and forums.
- **Incorporate Advanced Data Techniques:** Use concepts and relationship extraction to enrich the training dataset, enhancing the LLM's understanding of Kubernetes.
- **Open Source Contribution:** Release the fine-tuned model and dataset preparation tools.
Potentially work in tandem with the AMOS project on knowledge graph extraction to synergize both projects’ outcomes.
- **Benchmark Development:** Construct a manual benchmark to serve as ground truth for quantitatively evaluating the LLM's performance.

## Methodology

### Dataset Preparation

- **Data Sources:** Collect documentation from CNCF landscape project documentation, white papers, blog posts, and technical documents.
- **Preprocessing:** Normalize and structure the collected data.
- **Knowledge Extraction:** Use Named Entity Recognition (NER) to extract key entities and create relationships between them.

### LLM Fine-Tuning

- **LLM Selection:** Evaluate and select an appropriate open-source/open-model LLM based on performance, computational requirements, and licensing.
- **Fine-tuning Procedure:** Use the structured dataset for model training in a repeatable and reproducible manner, ideally using Cloud Native tools like KubeFlow and Kubernetes.

## Evaluation

- **Quantitative Metrics:** Use specific benchmarks such as BLEU score and Factual Question Accuracy to assess model performance.
- **Qualitative Evaluation:** Domain experts and project maintainers will evaluate the LLM’s comprehensiveness, accuracy, and clarity.


## Potential Impact

This project aims to become a definitive knowledge base for cloud computing, enriching the knowledge of engineers in cloud-native development and supporting the maintenance and growth of open-source projects.

## Get Involved!

To get started:
[TBD]
