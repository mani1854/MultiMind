from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import trace

from app.core.config import Settings


def setup_tracing(app: FastAPI, settings: Settings) -> None:
    resource = Resource.create({"service.name": settings.otel_service_name})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    FastAPIInstrumentor.instrument_app(app)

