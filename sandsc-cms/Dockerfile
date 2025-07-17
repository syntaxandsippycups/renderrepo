# Base image
FROM node:18

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install dependencies
RUN npm install

# ⚠️ Build the admin panel for production
RUN npm run build

# Expose the port Strapi runs on
EXPOSE 1337

# Start Strapi in production
CMD ["npm", "run", "start"]
