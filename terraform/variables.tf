variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "application_name" {
  description = "Name of the application"
  type        = string
  default     = "aux-analytics"
}

variable "flask_secret_key" {
  description = "Flask SECRET_KEY for the application"
  type        = string
  sensitive   = true
}

variable "your_ip" {
  description = "Your IP address for SSH access (CIDR notation)"
  type        = string
}
