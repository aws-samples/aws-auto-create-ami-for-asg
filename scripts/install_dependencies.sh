#!/bin/bash
sudo yum install httpd
sudo systemctl enable httpd.service
sudo chown -R $USER:$USER /var/www
sudo yum install php