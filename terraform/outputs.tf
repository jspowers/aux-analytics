output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.flask_app.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.flask_app.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.flask_app.public_dns
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.flask_app.id
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/aux-analytics-key ubuntu@${aws_instance.flask_app.public_ip}"
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_instance.flask_app.public_ip}"
}
