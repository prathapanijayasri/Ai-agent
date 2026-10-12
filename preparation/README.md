# Agent Preparation and Evaluation

This directory contains the system prompts and evaluation scripts used to test the Agent's reasoning, tool use, and conversation abilities.

## Evaluation
The evaluation script `evals/evaluate.py` runs through `test_cases.json` and deterministically checks if the agent chose the correct tool (or no tool) for the given scenarios.

To run:
```bash
export GOOGLE_API_KEY="your_key"
python evals/evaluate.py
```
