# OllamaForge: Model Submission Guidelines

Welcome to **OllamaForge**, an open-source platform for specialized language models using Ollama. Our platform is designed to help developers create, evaluate, and share highly specialized LLMs that excel at specific tasks. Below are the submission guidelines for contributing your specialized model.

### 1. **Model Submission**

To submit a specialized LLM, package your work as follows:

- **Modelfile**: Your Ollama model definition file that specifies:
  - Base model selection
  - System prompt
  - Model parameters
- **Benchmark Dataset**: Test cases in OpenAI chat format
- **Evaluation Metrics**: Quality and performance measurement code
- **Documentation**: Clear description of the model's specialization and use cases

### 2. **Evaluation Pipeline**

Once submitted, your model will enter an evaluation pipeline where it will be tested against task-specific benchmarks. The evaluation process includes:

- **Performance Metrics**:
  - **Quality**: Task-specific accuracy and appropriateness
  - **Latency**: Time to first token and inter-token latency
  - **Resource Usage**: Memory consumption
  - **Robustness**: Handling edge cases and unexpected inputs

- **Reward Model**: We use a specialized LLM to evaluate response quality, providing a score between 0-1 based on task-specific criteria.

### 3. **Benchmarking**

Models are evaluated using standardized benchmarks that include:
- Conversation test cases
- Expected outputs
- Performance thresholds
- Task-specific evaluation criteria

### 4. **Scoring and Badges**

After evaluation, models can earn different badges:
- 🚀 **Speed Champion**: Lowest latency
- 🎯 **Accuracy Master**: Highest quality scores
- 🪶 **Lightweight Leader**: Lowest memory footprint
- 🏆 **Overall Champion**: Best balance of metrics

These badges are displayed both in the repository and on Ollama Hub.

### 5. **Deployment to Ollama Hub**

Successful models are automatically:
1. Pushed to Ollama Hub
2. Made available via `ollama pull`
3. Tagged with earned badges
4. Credited to their creators

### 6. **Quality Control**

To maintain high standards:
- **One Task Per PR**: Changes must focus on a single task
- **Regular Evaluations**: Models are periodically re-evaluated
- **Community Feedback**: Users can provide feedback via GitHub issues
- **Continuous Integration**: Automated testing before deployment

### 7. **Future Plans**

Upcoming features:
- **GPU Metrics**: Evaluation of GPU performance and efficiency
- **Cross-Task Testing**: Evaluation across related tasks
- **A/B Testing**: Compare model variations
- **Enhanced Monitoring**: Detailed performance analytics

### 8. **Hub Features**

The OllamaForge platform includes:
- **Search/Filter**: Find models by task, performance metrics
- **Documentation**: Clear usage guides and examples
- **Leaderboards**: Track top performers in each category
- **Version Control**: Track model improvements over time

### 9. **Continuous Improvement**

OllamaForge is an evolving platform:
- **Version Tracking**: Monitor model improvements
- **Community Contributions**: Encourage enhancements
- **Recognition**: Showcase top contributors
- **Innovation**: Foster new specialized models

By participating in OllamaForge, you're helping create a hub of highly specialized, efficient language models that make AI more accessible and effective. We're excited to see your contributions!
