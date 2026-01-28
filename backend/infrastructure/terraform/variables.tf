variable "aws_region" {
  type = string
}

variable "instance_name" {
  description = "Value of the EC2 instance's Name tag."
  type        = string
}

variable "instance_type" {
  description = "The EC2 instance's type."
  type        = string
}

variable "key_name" {
 description = "SSH key pair name"
 type        = string
}

variable "profile" {
 description = "AWS profile name"
 type        = string
}