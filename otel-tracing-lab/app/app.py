from flask import Flask
import random
import time

# OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)

from opentelemetry.instrumentation.flask import FlaskInstrumentor

# -----------------------------
# OTel Setup
# -----------------------------

resource = Resource.create({
    "service.name": "signup-api"
})

provider = TracerProvider(resource=resource)

trace.set_tracer_provider(provider)

otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)

provider.add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)

# -----------------------------
# Flask App
# -----------------------------

app = Flask(__name__)

FlaskInstrumentor().instrument_app(app)

# -----------------------------
# Routes
# -----------------------------

@app.route("/")
def home():

    with tracer.start_as_current_span("home-custom-span"):

        sleep_time = random.uniform(0.1, 1.5)

        time.sleep(sleep_time)

        return {
            "message": "OTel tracing works",
            "sleep_time": sleep_time
        }


@app.route("/slow")
def slow():

    with tracer.start_as_current_span("slow-operation"):

        time.sleep(3)

        return {
            "message": "slow endpoint finished"
        }


@app.route("/error")
def error():

    with tracer.start_as_current_span("error-operation"):

        raise Exception("fake application error")


# -----------------------------

app.run(
    host="0.0.0.0",
    port=5000
)