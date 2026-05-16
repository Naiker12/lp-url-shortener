variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
}

variable "project_name" {
  description = "Project prefix used to name AWS resources."
  type        = string
}

variable "base_url" {
  description = "Public base URL used to build shortened URLs."
  type        = string
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for URL records."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}
