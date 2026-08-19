"""
metrics.py — Enterprise Prometheus Metrics Collector
=====================================================
WHAT THIS DOES:
  Collects and exports standard Prometheus-format metrics:
  - HTTP Request throughput and latency distributions
  - Multi-agent execution counts and failure rates
  - Vector similarity search query volume
  - Automated workflow execution totals
"""

from collections import defaultdict
import time


class MetricsCollector:
    """
    In-process Prometheus metrics aggregator.
    Maintains counters and histograms for enterprise telemetry.
    """

    def __init__(self) -> None:
        # Counters: (method, path, status) -> count
        self.http_requests_total: dict[tuple[str, str, int], int] = defaultdict(int)
        # Latency buckets
        self.request_durations: list[float] = []
        # Agent execution counts: (agent_name, status) -> count
        self.agent_executions_total: dict[tuple[str, str], int] = defaultdict(int)
        # RAG searches: workspace_id -> count
        self.rag_queries_total: dict[str, int] = defaultdict(int)
        # Workflow runs: status -> count
        self.workflow_runs_total: dict[str, int] = defaultdict(int)
        self.start_time = time.time()

    def record_http_request(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        """Records an HTTP request outcome and latency."""
        # Sanitize path to avoid cardinality explosion
        clean_path = path.split("?")[0]
        if clean_path.startswith("/api/v1/documents/") and len(clean_path.split("/")) > 4:
            clean_path = "/api/v1/documents/{id}"
        elif clean_path.startswith("/api/v1/workflows/runs/") and len(clean_path.split("/")) > 4:
            clean_path = "/api/v1/workflows/runs/{id}"

        self.http_requests_total[(method.upper(), clean_path, status_code)] += 1
        self.request_durations.append(duration_seconds)
        if len(self.request_durations) > 1000:
            self.request_durations = self.request_durations[-1000:]

    def record_agent_execution(self, agent_name: str, status: str) -> None:
        """Records an agent execution step."""
        self.agent_executions_total[(agent_name, status)] += 1

    def record_rag_query(self, workspace_id: str) -> None:
        """Records a semantic search operation."""
        self.rag_queries_total[workspace_id] += 1

    def record_workflow_run(self, status: str) -> None:
        """Records an automated workflow run."""
        self.workflow_runs_total[status] += 1

    def export_prometheus(self) -> str:
        """Generates valid Prometheus text-format exposition."""
        lines = [
            "# HELP multimind_uptime_seconds Total seconds since process startup",
            "# TYPE multimind_uptime_seconds gauge",
            f"multimind_uptime_seconds {time.time() - self.start_time:.2f}",
            "",
            "# HELP multimind_http_requests_total Total number of HTTP requests processed",
            "# TYPE multimind_http_requests_total counter",
        ]

        for (method, path, status), count in sorted(self.http_requests_total.items()):
            lines.append(
                f'multimind_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
            )

        lines.extend([
            "",
            "# HELP multimind_http_request_duration_seconds_avg Average HTTP request latency in seconds",
            "# TYPE multimind_http_request_duration_seconds_avg gauge",
        ])
        avg_latency = (
            sum(self.request_durations) / len(self.request_durations)
            if self.request_durations
            else 0.0
        )
        lines.append(f"multimind_http_request_duration_seconds_avg {avg_latency:.4f}")

        lines.extend([
            "",
            "# HELP multimind_agent_executions_total Number of specialist agent executions",
            "# TYPE multimind_agent_executions_total counter",
        ])
        for (agent_name, status), count in sorted(self.agent_executions_total.items()):
            lines.append(
                f'multimind_agent_executions_total{{agent="{agent_name}",status="{status}"}} {count}'
            )

        lines.extend([
            "",
            "# HELP multimind_rag_queries_total Total semantic search queries",
            "# TYPE multimind_rag_queries_total counter",
        ])
        for ws_id, count in sorted(self.rag_queries_total.items()):
            lines.append(f'multimind_rag_queries_total{{workspace="{ws_id}"}} {count}')

        lines.extend([
            "",
            "# HELP multimind_workflow_runs_total Total workflow engine executions",
            "# TYPE multimind_workflow_runs_total counter",
        ])
        for status, count in sorted(self.workflow_runs_total.items()):
            lines.append(f'multimind_workflow_runs_total{{status="{status}"}} {count}')

        return "\n".join(lines) + "\n"


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    return metrics_collector
