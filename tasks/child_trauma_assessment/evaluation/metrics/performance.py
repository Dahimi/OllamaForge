import time
import psutil
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass
from ollama import chat


@dataclass
class LatencyMetrics:
    time_to_first_token: float  # seconds
    inter_token_latencies: List[float]  # list of latencies between tokens
    avg_inter_token_latency: float
    total_response_time: float
    
    
@dataclass
class MemoryMetrics:
    peak_memory_mb: float
    avg_memory_mb: float
    memory_samples: List[float]


@dataclass
class PerformanceMetrics:
    latency: LatencyMetrics
    memory: MemoryMetrics


def measure_performance(model_name: str, messages: List[Dict], sample_interval: float = 0.1) -> PerformanceMetrics:
    """
    Measures performance metrics while running model inference.
    
    Args:
        model_name: Name of the Ollama model
        messages: List of conversation messages
        sample_interval: Interval for memory sampling in seconds
    
    Returns:
        PerformanceMetrics containing latency and memory measurements
    """
    process = psutil.Process()
    memory_samples = []
    inter_token_times = []
    last_token_time = None
    
    # Start timing
    start_time = time.time()
    first_token_received = False
    time_to_first_token = None
    
    # Start streaming response
    stream = chat(
        model=model_name,
        messages=messages,
        stream=True,
    )
    
    # Process stream and collect metrics
    for chunk in stream:
        current_time = time.time()
        
        # Memory sampling
        memory_mb = process.memory_info().rss / 1024 / 1024
        memory_samples.append(memory_mb)
        
        # First token timing
        if not first_token_received:
            time_to_first_token = current_time - start_time
            first_token_received = True
        
        # Inter-token latency
        if last_token_time is not None:
            inter_token_times.append(current_time - last_token_time)
        last_token_time = current_time
        
        time.sleep(sample_interval)  # Allow time for memory sampling
    
    total_time = time.time() - start_time
    
    # Calculate memory metrics
    memory_metrics = MemoryMetrics(
        peak_memory_mb=max(memory_samples),
        avg_memory_mb=statistics.mean(memory_samples),
        memory_samples=memory_samples
    )
    
    # Calculate latency metrics
    latency_metrics = LatencyMetrics(
        time_to_first_token=time_to_first_token,
        inter_token_latencies=inter_token_times,
        avg_inter_token_latency=statistics.mean(inter_token_times) if inter_token_times else 0,
        total_response_time=total_time
    )
    
    return PerformanceMetrics(
        latency=latency_metrics,
        memory=memory_metrics
    )


def format_performance_report(metrics: PerformanceMetrics) -> str:
    """
    Formats performance metrics into a readable report.
    """
    report = f"""Performance Metrics Report:

Latency:
--------
Time to First Token: {metrics.latency.time_to_first_token:.3f}s
Average Inter-token Latency: {metrics.latency.avg_inter_token_latency:.3f}s
Total Response Time: {metrics.latency.total_response_time:.3f}s

Memory Usage:
------------
Peak Memory: {metrics.latency.peak_memory_mb:.2f}MB
Average Memory: {metrics.latency.avg_memory_mb:.2f}MB
"""
    return report 