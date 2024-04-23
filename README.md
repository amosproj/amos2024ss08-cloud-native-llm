![plot](/Deliverables/sprint-01/team-logo.png)

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

The primary goal focuses on developing a Cloud Native focused fine-tuned Large Language Model (LLM) that capable of answering complex queries about Kubernetes installations.

By providing immediate, context-aware answers and guidance, this project reduces the learning curve and increases productivity in managing Kubernetes installations.

Hence, it will be further developed to create AI assistants that will aid developers in navigating and managing Kubernetes environments.

The project is open sourced and open modeled to be used by the [community](https://www.kubermatic.com/company/community/).

The folder structure is as follows:
[TBD]
- **First** 1.
- **Second** 2.
- **Third:** 3.


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

- **LLM Selection:** Evaluate and select an appropriate open-source/open model LLM based on performance, computational requirements, and licensing.
- **Fine-tuning Procedure:** Use the structured dataset for model training in a repeatable and reproducible manner, ideally using Cloud Native tools like KubeFlow and Kubernetes.

## Evaluation

- **Quantitative Metrics:** Use specific benchmarks such as BLEU score and Factual Question Accuracy to assess model performance.
- **Qualitative Evaluation:** Domain experts and project maintainers will evaluate the LLM’s comprehensiveness, accuracy, and clarity.


## Potential Impact

This project aims to become a definitive knowledge base for cloud computing, enriching the knowledge of engineers in cloud-native development and supporting the maintenance and growth of open-source projects.

## Get Involved!

To get started:
[TBD]
