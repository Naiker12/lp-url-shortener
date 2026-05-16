variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project prefix used to name AWS resources."
  type        = string
  default     = "lp-url-shortener"
}

variable "base_url" {
  description = "Public base URL used to build shortened URLs."
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for URL records."
  type        = string
  default     = "urls"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}
