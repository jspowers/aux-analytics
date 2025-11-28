output "instance_public_ip" {
  description = "Public IP address of EC2 instance"
  value       = aws_instance.flask_app.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of EC2 instance"
  value       = aws_instance.flask_app.public_dns
}

output "domain_name" {
  description = "Domain name for application"
  value       = var.domain_name
}

output "ssh_command" {
  description = "SSH command to connect to instance"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.flask_app.public_ip}"
}
