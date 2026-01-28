output "instance_public_ip" {
  description = "The dynamic public IP of the app server"
  value       = aws_instance.backend.public_ip
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.backend.public_ip}"
}
