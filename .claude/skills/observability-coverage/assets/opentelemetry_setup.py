import logging

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor, RequestInfo
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span

logger = logging.getLogger(__name__)

METRIC_EXPORT_INTERVAL_MS = 15_000


def build_meter_provider(resource: Resource, endpoint: str) -> MeterProvider:
    metric_exporter = OTLPMetricExporter(
        endpoint=endpoint,
        insecure=True,
    )

    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        export_interval_millis=METRIC_EXPORT_INTERVAL_MS,
    )

    return MeterProvider(resource=resource, metric_readers=[metric_reader])


def set_httpx_span_name(span: Span, request: RequestInfo) -> None:
    if not span or not span.is_recording():
        return

    method = request.method.decode() if isinstance(request.method, bytes) else request.method
    host = request.url.host

    span.update_name(f"{method} {host}" if host else method)


def httpx_request_hook(span: Span, request: RequestInfo) -> None:
    set_httpx_span_name(span, request)


async def httpx_async_request_hook(span: Span, request: RequestInfo) -> None:
    set_httpx_span_name(span, request)


def setup_opentelemetry(
    service_name: str,
    endpoint: str | None,
    *,
    environment: str = "local",
    export_traces: bool = False,
    export_metrics: bool = False,
) -> TracerProvider:
    resource = Resource.create(
        {
            "service.name": service_name,
            "deployment.environment": environment,
        }
    )

    provider = TracerProvider(resource=resource)

    if export_traces and endpoint:
        otlp_exporter = OTLPSpanExporter(
            endpoint=endpoint,
            insecure=True,
        )

        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)

    if export_metrics and endpoint:
        metrics.set_meter_provider(
            build_meter_provider(
                resource=resource,
                endpoint=endpoint,
            )
        )

    LoggingInstrumentor().instrument(
        set_logging_format=True,
        log_level=logging.INFO,
    )
    HTTPXClientInstrumentor().instrument(
        request_hook=httpx_request_hook,
        async_request_hook=httpx_async_request_hook,
    )
    SQLAlchemyInstrumentor().instrument()

    logger.info(
        "OpenTelemetry configured",
        extra={
            "service_name": service_name,
            "environment": environment,
            "export_traces": export_traces,
            "export_metrics": export_metrics,
        },
    )

    return provider


def get_current_trace_id() -> str | None:
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, "032x")

    return None


def get_current_span_id() -> str | None:
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().span_id, "016x")

    return None
