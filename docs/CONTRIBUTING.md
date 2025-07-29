# Contributing to OllamaForge

## Vision
We're building the world's first competitive hub for specialized LLMs, forged with Ollama. Think of it as an Olympic Games for AI models - where each task is a different sport, and models compete to be the fastest, most accurate, or most efficient.

## Important Rules 📜

### One Task Per PR
To maintain clean evaluation pipelines and clear performance tracking:
- Each PR must modify only ONE task
- Changes to multiple tasks must be split into separate PRs
- Task template updates are exempt from this rule

This ensures:
- Clean performance comparisons
- Independent task evolution
- Clear attribution of improvements
- Focused review process

## Task Categories and Badges 🏆

Each task in our hub can have multiple champions, recognized with distinct badges:

- 🚀 **Speed Champion**: Lowest latency (TTFT + token generation)
- 🎯 **Accuracy Master**: Highest quality scores
- 🪶 **Lightweight Leader**: Lowest memory footprint
- 🏆 **Overall Champion**: Best balance of all metrics

These badges are automatically awarded based on performance metrics and are displayed both in the repository and on Ollama Hub.

## Types of Contributions

### 1. New Task Submissions
To submit a new specialized LLM task:

1. **Task Directory Structure**:
   ```
   tasks/your_task_name/
   ├── model/
   │   └── Modelfile           # Ollama model definition
   ├── benchmarks/
   │   └── test_cases.json    # Test cases and expected outputs
   └── evaluation/
       ├── metrics/           # Custom metrics if needed
       └── README.md          # Task-specific documentation
   ```

2. **Required Components**:
   - Modelfile with clear system prompt and parameters
   - Benchmark dataset with test cases
   - Evaluation metrics (or use standard ones)
   - Documentation explaining the task

3. **Quality Standards**:
   - Clear task definition and use case
   - Comprehensive benchmark dataset
   - Performance metrics implementation
   - Thorough documentation

### 2. Improving Existing Tasks

Want to dethrone the current champion? Here's how:

1. **Model Improvements**:
   - Enhance the Modelfile
   - Optimize system prompts
   - Fine-tune parameters
   - Try different base models

2. **Benchmark Enhancements**:
   - Add more challenging test cases
   - Improve expected outputs
   - Add edge cases
   - Contribute domain expertise

3. **Metric Improvements**:
   - Add new evaluation metrics
   - Enhance existing metrics
   - Improve performance tracking

## The Path to Ollama Hub 🌟

When your PR is successful:
1. Your model is automatically pushed to Ollama Hub
2. It becomes instantly available worldwide via `ollama pull`
3. Your achievements (badges) are displayed on the model page
4. You're credited as the model creator/contributor

## Submission Process

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Nexus-LLM-Hub.git
   cd Nexus-LLM-Hub
   ```

2. **Create Branch**:
   ```bash
   git checkout -b task/your-task-name
   ```

3. **Local Testing**:
   ```bash
   # Install dependencies
   pip install -r requirements/requirements.txt
   
   # Test your task
   cd tasks/your_task_name
   python evaluation/run_evaluation.py
   ```

4. **Submit PR**:
   - Clear description of changes
   - Performance improvements demonstrated
   - All tests passing

## PR Requirements

Your PR must demonstrate at least ONE of these:

1. **Quality Champion** 🎯
   - Response quality score > current best
   - Clear improvement in task-specific metrics
   - No significant performance regression

2. **Speed Demon** 🚀
   - Lower TTFT than current best
   - Better token generation speed
   - Quality score within 5% of best

3. **Resource Master** 🪶
   - Lower memory usage
   - Smaller model size
   - Quality score within 5% of best

## Code Style and Best Practices
- Use Python 3.11+
- Follow PEP 8
- Include type hints
- Document functions and classes
- Add comprehensive tests

## The Review Process

1. **Automated Evaluation**:
   - Quality metrics
   - Performance benchmarks
   - Resource usage tracking

2. **Badge Assignment**:
   - Automatic comparison with current leaders
   - Badge updates if new records are set
   - Multiple badges possible for one model

3. **Ollama Hub Integration**:
   - Automatic push on successful PR
   - Badge display on Hub
   - Usage statistics tracking

## Getting Help

Feel free to:
- Open issues for questions
- Join our Discord community
- Check our detailed guides
- Ask for mentor support

Remember: Every champion started as a challenger. Your model could be next! 🚀

## Code of Conduct
- Be respectful and constructive
- Give credit where due
- Help others succeed
- Celebrate achievements

## Questions?
Feel free to open an issue for:
- Task proposal discussions
- Technical questions
- Feature requests
- Bug reports 