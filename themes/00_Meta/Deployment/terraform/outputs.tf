# Terraform Outputs
# =================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "api_endpoint" {
  description = "API endpoint URL"
  value       = "https://api.${var.domain_name}"
}

output "ecr_repository_urls" {
  description = "ECR repository URLs"
  value = {
    api    = aws_ecr_repository.api.repository_url
    worker = aws_ecr_repository.worker.repository_url
    ml     = aws_ecr_repository.ml.repository_url
  }
}

output "rds_endpoint" {
  description = "RDS Aurora cluster endpoint"
  value       = aws_rds_cluster.main.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
  sensitive   = true
}
