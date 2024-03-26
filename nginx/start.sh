#!/bin/bash

# Start NGINX in the background
nginx -g 'daemon off;' &

# Obtain SSL certificates
# Note: You need to replace your_domain.com with your actual domain name
certbot --nginx -d api.alicia.nortedev.net --non-interactive --agree-tos -m dylan@nortedev.net --redirect

# Keep the container running
wait
