#!/usr/bin/env python3

import json
import sys
import os
from typing import Tuple
from pathlib import Path
import importlib.util
from ollama import chat

def get_task_metrics(task_path: str) -> Tuple[object, object]:
    """
    Dynamically import the task's metric modules.
    """
    metrics_path = Path(task_path) / "evaluation" / "metrics"
    
    # Import quality metrics
    quality_spec = importlib.util.spec_from_file_location(
        "response_quality",
        metrics_path / "response_quality.py"
    )
    quality_module = importlib.util.module_from_spec(quality_spec)
    quality_spec.loader.exec_module(quality_module)
    
    # Import performance metrics
    perf_spec = importlib.util.spec_from_file_location(
        "performance",
        metrics_path / "performance.py"
    )
    perf_module = importlib.util.module_from_spec(perf_spec)
    perf_spec.loader.exec_module(perf_module)
    
    return quality_module, perf_module


def evaluate_task(task_path: str, model_name: str) -> Tuple[float, float, float, float]:
    """
    Evaluate a specific task's model.
    
    Returns:
        Tuple of (avg_quality, avg_ttft, avg_token_latency, avg_memory)
    """
    # Load task-specific metrics
    quality_module, perf_module = get_task_metrics(task_path)
    
    # Load benchmark cases
    with open(os.path.join(task_path, 'benchmarks', 'test_cases.json'), 'r') as f:
        test_cases = json.load(f)['test_cases']
    
    quality_scores = []
    performance_metrics = []
    
    # Run evaluation for each test case
    for case in test_cases:
        # Measure performance
        perf_metrics = perf_module.measure_performance(
            model_name=model_name,
            messages=case['conversation']
        )
        performance_metrics.append(perf_metrics)
        
        # Get model response (non-streaming for quality evaluation)
        response = chat(
            model=model_name,
            messages=case['conversation'],
            stream=False
        )
        
        # Evaluate quality
        quality_metric = quality_module.evaluate_response_quality(
            conversation_history=case['conversation'],
            model_response=response.message.content,
            expected_output=case['expected_output']
        )
        quality_scores.append(quality_metric)
    
    # Calculate average scores
    avg_quality = sum(score.score for score in quality_scores) / len(quality_scores)
    avg_ttft = sum(p.latency.time_to_first_token for p in performance_metrics) / len(performance_metrics)
    avg_token_latency = sum(p.latency.avg_inter_token_latency for p in performance_metrics) / len(performance_metrics)
    avg_memory = sum(p.memory.avg_memory_mb for p in performance_metrics) / len(performance_metrics)
    
    return avg_quality, avg_ttft, avg_token_latency, avg_memory


def print_results(metrics: Tuple[float, float, float, float]):
    """Print evaluation results in a formatted way."""
    avg_quality, avg_ttft, avg_token_latency, avg_memory = metrics
    
    print("\nEvaluation Results:")
    print(f"Average Quality Score: {avg_quality:.3f}")
    print(f"Average Time to First Token: {avg_ttft:.3f}s")
    print(f"Average Inter-token Latency: {avg_token_latency:.3f}s")
    print(f"Average Memory Usage: {avg_memory:.2f}MB")


def main():
    if len(sys.argv) != 3:
        print("Usage: evaluate_task.py <task_path> <model_name>")
        sys.exit(1)
        
    task_path = sys.argv[1]
    model_name = sys.argv[2]
    
    try:
        metrics = evaluate_task(task_path, model_name)
        print_results(metrics)
        
        # Exit based on quality threshold
        QUALITY_THRESHOLD = 0.8
        sys.exit(0 if metrics[0] >= QUALITY_THRESHOLD else 1)
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 