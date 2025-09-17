# AI Template - Python FastAPI Service

A Python FastAPI service template with Eureka service discovery integration for microservices architecture.

## Eureka Service Discovery Configuration

This project is configured as a Eureka client that automatically registers with the Eureka service registry. The service runs on port 8000 and registers itself as `python-ai-service`.

### Eureka Client Implementation

The Eureka integration is implemented in `src/config/eureka_config.py`:

- **Service registration**: Automatic registration with Eureka server during startup
- **Health checks**: Integrated health check endpoints (`/actuator/health`)
- **Graceful shutdown**: Automatic deregistration during application shutdown
- **Authentication**: Support for Eureka server authentication via credentials

### Gateway Configuration

For integration into the microservices architecture, the following configuration needs to be added:

#### 1. SA-Gateway Application.yml

In `sa-gateway/application.yml`:

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: ai-template
          uri: lb://ai-template
          predicates:
            - Path=/ai-template/**
          filters:
            - StripPrefix=1
            - LegacyAuthentication
```

#### 2. Service Configuration

Create a new directory `ai-template` with `ai-template/application.yml`:

```yaml
server:
  port: 8000
  servlet:
    context-path: /python-ai-service

security.basic.enabled: false
```

### Service Discovery Details

- **Service name**: `python-ai-service`
- **Port**: 8000
- **Context path**: `/python-ai-service`
- **Health endpoint**: `/actuator/health`
- **Status endpoint**: `/actuator/info`

### Environment Variables

The Eureka client can be configured via environment variables:

```bash
EUREKA_USERNAME=dev
EUREKA_PASSWORD=dev
```

Or via direct parameters in the code:

```python
init_eureka_client(port=8000, username="dev", password="dev")
```

### Service Lifecycle

1. **Startup**: Service registers itself with Eureka server
2. **Runtime**: Service remains registered and responds to health checks
3. **Shutdown**: Service automatically deregisters itself from Eureka server

This configuration ensures that the Python service seamlessly integrates into the microservices architecture via Eureka service discovery.
