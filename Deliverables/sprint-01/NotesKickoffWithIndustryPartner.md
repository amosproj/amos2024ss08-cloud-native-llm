# Notes on the Kickoff with our Industry Partner Kubermatic

## Participants
- Three Stackholders (functional and technical) from Kubermatic
- Dominic Fischer (PO), Jiaao Li (PO)
- All six developers of the team

## Tools for communication between Kubermatic and us
- Slack: We therefore will send them our user email addresses
- Meetings: Google Calender of our main communication partner from Kubermatic will be shared to us by a link so that we can make appointments, usage of Google Meet
- Our Main Communication Partner will participate in our Plannings and Retros
- Next appointment to collect requirements is set for Monday 5:30pm

## Kubermatic background
- Open Source Development in infrastructure space
- Cloud Native Kubernetes background
- building a platform for running and managing a Kubernetes platform for multiple data centers
- Google Meet GitHub for communicationI
- ChaosGPT is an already existing tool, but that is not that much fine-tuned for the use case

## Goal of the product
- dedicated cloud native LLM
- that is able to be executed on Kubernetes
- The executable model is the product, no frontend required
  build reference architecture to share
- help to define the blueprint for the AI infrastructure world
- Supported Language: English

## Dataset
- Dataset should be publicly available
- recommended leave Data sets on hugging space
- Datasets should be created more or less automatically
- Prior Goal for dataset, use documentation of official documents (".md", ".pdf")
- Use landscape (the configuration in yml/yaml files)

## Base Model
- OpenModel would be nice
- No Model that requires a license
- marker: Biases
- Check legal issues using the Model, legal resources from Kubermatic if required
- maybe Kubermatic can help us get resources from Google as they are also interested in the outcome of this project (as large user of Kubernetes), also Gemma
- only use openly available models
- no license impact on output model (very important, but eventually not a must)
- Check what would be the best suitable model
- does not need to be to big, choose model that is good working on small datasets
- for Gemma some resources could be available including some testing set from google, but of course not directly for our use case

## Kubeflow
- Machine Learning Platform for inside Kubernetes
- use is recommended

## Model Evaluatoin
- Challenge the model itself
- Kubermatic would reach out to the maintainers or specialists to test the model
- Manuel tests by (domain) experts
- First model evaluation for hallucinations
- Point score afterwards would be a good to have (but focus is definitely on hallucinations)
- Model should have very specific domain knowledge not "tell us how the weather is"

## Notes
- There are some environments where data is not allowed to leave the data center / communication with the outside is not possible
