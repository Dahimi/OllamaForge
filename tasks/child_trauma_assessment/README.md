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

## Directory Structure
```
child_trauma_assessment/
├── model/
│   └── Modelfile           # Ollama model definition
├── benchmarks/
│   └── test_cases.json     # Benchmark conversations and expected outputs
└── evaluation/
    ├── reward_model/       # Quality assessment model
    └── metrics/
        ├── response_quality.py  # Evaluation metrics
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
- Evaluation criteria

## Evaluation Criteria

### Response Quality
Responses are evaluated on:
1. Clinical Accuracy
2. Safety & Urgency Recognition
3. Empathy & Tone
4. Actionable Guidance
5. Professional Boundaries

### Performance Metrics
The model is also evaluated on performance characteristics:
1. Latency
   - Time to First Token (TTFT)
   - Inter-token Latency
   - Total Response Time
2. Memory Usage
   - Peak Memory Consumption
   - Average Memory Usage

## CI/CD Pipeline
The repository includes an automated evaluation pipeline that runs on every PR:
1. Builds the model using the PR's Modelfile
2. Runs all benchmark test cases
3. Measures both quality and performance metrics
4. Enforces quality threshold (currently 0.8)

PR requirements:
- Quality score >= 0.8
- No regression in performance metrics
- All test cases must pass

## Contributing
To contribute improvements:
1. Fork the repository
2. Modify the Modelfile or add benchmark cases
3. Test locally using Ollama
4. Submit a PR

Your PR must demonstrate:
- Improved response quality scores
- Maintained or improved latency
- No regression in existing test cases

### Local Testing
To test your changes locally:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Create and serve your model
ollama create my-trauma-model -f ./model/Modelfile
ollama serve

# Install Python dependencies
pip install -r requirements.txt

# Run evaluation
python evaluation/run_evaluation.py
```


## Safety Notes
- This model is NOT a replacement for professional mental health care
- High-risk cases are flagged for immediate professional attention
- Cultural sensitivity is maintained throughout responses 