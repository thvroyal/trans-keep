/**
 * OpenTelemetry Web SDK configuration for TransKeep frontend
 * 
 * Initializes distributed tracing for the React application,
 * sending traces to Jaeger collector for development.
 */

import { BasicTracerProvider, SimpleSpanProcessor } from '@opentelemetry/sdk-trace-web'
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http'
import { Resource } from '@opentelemetry/resources'
import { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } from '@opentelemetry/semantic-conventions'
import { trace } from '@opentelemetry/api'

/**
 * Initialize OpenTelemetry Web SDK with Jaeger exporter
 * 
 * @param serviceName - Name of the service for trace identification
 * @param collectorUrl - OTLP HTTP collector endpoint URL
 */
export function initTelemetry(
  serviceName: string = 'transkeep-frontend',
  collectorUrl: string = 'http://localhost:4318/v1/traces'
): void {
  // Create OTLP exporter for sending traces
  const exporter = new OTLPTraceExporter({
    url: collectorUrl,
  })

  // Create resource with service name and metadata
  const resource = Resource.default().merge(
    new Resource({
      [ATTR_SERVICE_NAME]: serviceName,
      [ATTR_SERVICE_VERSION]: '0.1.0',
    })
  )

  // Create tracer provider with resource
  const tracerProvider = new BasicTracerProvider({
    resource: resource,
  })

  // Add exporter as span processor
  tracerProvider.addSpanProcessor(new SimpleSpanProcessor(exporter))

  // Set global tracer provider
  tracerProvider.register()

  console.log(`✓ OpenTelemetry initialized for ${serviceName}`)
}

/**
 * Get current tracer for creating custom spans
 * 
 * @param name - Module name or identifier for the tracer
 * @returns Tracer instance for custom instrumentation
 */
export function getTracer(name: string = 'transkeep-app') {
  return trace.getTracer(name)
}

/**
 * Get trace ID from current context (for logging correlation)
 * 
 * @returns Current trace ID as hex string, or undefined if not in trace
 */
export function getCurrentTraceId(): string | undefined {
  // This would be populated by the tracer when in an active span
  // For now, return undefined - will be enhanced with context API
  return undefined
}
