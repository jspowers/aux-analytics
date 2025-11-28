variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "SSH key pair name for EC2 access"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "auxanalytics.com"
}

variable "app_password" {
  description = "Application password for authentication"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Flask secret key"
  type        = string
  sensitive   = true
}

variable "github_repo_url" {
  description = "GitHub repository URL for application code"
  type        = string
  default     = "https://github.com/yourusername/aux-analytics.git"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH (your IP)"
  type        = string
  default     = "0.0.0.0/0"  # CHANGE THIS to your IP for security

  validation {
    condition     = can(cidrhost(var.allowed_ssh_cidr, 0))
    error_message = "The allowed_ssh_cidr must be a valid IPv4 CIDR block (e.g., 192.168.1.0/24 or 10.0.0.1/32)."
  }
}
