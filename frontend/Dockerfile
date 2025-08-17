# Frontend Dockerfile for RAGTube shadcn/ui + Vite frontend
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 8501

# Start Vite development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
