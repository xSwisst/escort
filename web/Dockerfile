FROM node:20-alpine AS builder

WORKDIR /app

RUN apk add --no-cache libc6-compat

# Copy package manifests and install dependencies
COPY web/package*.json ./
RUN npm ci

# Copy project files and build static export
COPY web/ ./
RUN npm run build

# Production stage: lightweight Nginx
FROM nginx:alpine

# Install curl for container healthcheck
RUN apk add --no-cache curl

# Default environment variables for template substitution
ENV PORT=8007
ENV WEB_DOMAIN=_
ENV APP_NAME="ELEGANT AGENCY"
ENV BOT_USERNAME="@ElegantAgencyApp"
ENV BOT_URL="https://t.me/ElegantAgencyApp"
ENV SUPPORT_BOT_URL="https://t.me/ElegantAgencySupportApp"
ENV WEB_APP_URL="https://app.elegant-agency.fun"
ENV CONTACT_EMAIL=""

# Copy custom Nginx configuration template for automatic envsubst
COPY web/nginx.conf /etc/nginx/templates/default.conf.template

# Copy static build output
COPY --from=builder /app/out /usr/share/nginx/html

EXPOSE 8007

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8007/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
