# Firm Ecosystem — Terraform Module

Deploy the Firm Ecosystem to AWS ECS Fargate, Google Cloud Run, or Azure Container Apps.

## Quick Start (AWS)

```hcl
module "firm" {
  source = "./deploy/terraform"

  provider_name = "aws"
  region        = "eu-west-1"
  firm_version  = "3.3.0"

  # Optional
  enable_memory_server = true
  mcp_port             = 8012
  memory_port          = 8765
}

output "mcp_url" {
  value = module.firm.mcp_endpoint
}
```

```bash
cd deploy/terraform
terraform init
terraform plan
terraform apply
```

## Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `provider_name` | string | `"aws"` | Cloud provider: aws, gcp, azure |
| `region` | string | `"us-east-1"` | Deployment region |
| `firm_version` | string | `"3.3.0"` | Docker image version tag |
| `mcp_port` | number | `8012` | MCP server port |
| `memory_port` | number | `8765` | Memory server port |
| `enable_memory_server` | bool | `true` | Deploy memory server alongside MCP |
| `cpu` | number | `512` | CPU units (256, 512, 1024, 2048) |
| `memory` | number | `1024` | Memory in MB |
| `environment` | map(string) | `{}` | Extra environment variables |

## Outputs

| Output | Description |
|--------|-------------|
| `mcp_endpoint` | Full URL to the MCP server |
| `memory_endpoint` | Full URL to the memory server |
| `service_name` | Cloud service name for CLI management |

## Supported Providers

- **AWS**: ECS Fargate + ALB + CloudWatch
- **GCP**: Cloud Run (TODO)
- **Azure**: Container Apps (TODO)

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
