# Child Trauma Assessment Model

## Overview
This specialized LLM is designed to assist in the psychological assessment of children in conflict zones. It provides trauma-informed responses to caregivers while maintaining appropriate professional boundaries and safety protocols.

## Model Details
- Base Model: Gemma 3B
- Specialization: Child trauma assessment and support
- Primary Use Cases:
  - Initial trauma screening
  - Coping strategy recommendations
  - Urgent case identification
  - Ongoing support guidance
  - Report generation

## Directory Structure
```
child_trauma_assessment/
├── model/
│   └── Modelfile           # Ollama model definition
├── benchmarks/
│   └── test_cases.json     # Benchmark conversations and expected outputs
└── evaluation/
    └── metrics/
        ├── reward_model.py  # Quality assessment model and metrics
        └── performance.py      # Performance tracking
```

## Benchmark Dataset
The benchmark includes various scenarios:
- Initial assessment conversations
- Follow-up support requests
- High-risk case identification
- Cultural sensitivity scenarios

Each test case includes:
- Conversation history
- Expected model responses
