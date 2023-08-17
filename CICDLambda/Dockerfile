# Use an official Node.js runtime as the base image
FROM node:14-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working director

# Install dependencies
RUN npm install

# Copy the application code to the container
COPY . .

# Expose a port that the application listens on
EXPOSE 3000

# Define the command to run the application
CMD [ "npm", "start" ]