# Deployment

## Docker Compose

Use Docker Compose for local development and demos:

```bash
docker compose up --build
```

## Kubernetes

The manifests in `infra/k8s` are intentionally minimal and ready to adapt for a managed cluster:

```bash
kubectl apply -f infra/k8s/
```

Production recommendations:

- Move secrets to External Secrets, Vault, AWS Secrets Manager, or GCP Secret Manager.
- Use managed PostgreSQL and Redis.
- Run Qdrant with persistent volumes and replication.
- Add ingress, TLS, autoscaling, network policies, and pod disruption budgets.
- Route OpenTelemetry to a managed observability backend.

