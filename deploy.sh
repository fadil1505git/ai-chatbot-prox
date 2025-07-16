#!/bin/bash
echo "🚀 Mula deploy AI Chatbot..."

# Tarik semua image terkini
docker compose pull

# Build projek
docker compose build

# Jalankan
docker compose up -d

# Semak status
docker compose ps

echo "✅ Deploy selesai!"
