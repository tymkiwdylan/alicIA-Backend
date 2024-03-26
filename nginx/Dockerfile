# Use the official NGINX image as a parent image
FROM nginx:latest

# Copy the custom NGINX config into the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port NGINX is listening on
EXPOSE 80

# Start NGINX
CMD ["nginx", "-g", "daemon off;"]
