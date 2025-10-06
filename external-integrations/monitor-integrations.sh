#!/bin/bash
# Script para monitorar status das integrações externas

echo "📊 Monitorando integrações externas..."

REDIS_HOST=${REDIS_HOST:-localhost}
REDIS_PORT=${REDIS_PORT:-6379}

# Verificar conectividade das APIs
check_api_connectivity() {
    local api_name=$1
    local url=$2
    
    if curl -s --head --request GET --connect-timeout 5 "$url" > /dev/null; then
        echo "✅ $api_name: Online"
        redis-cli -h $REDIS_HOST -p $REDIS_PORT SET "external:${api_name}:status" "online"
    else
        echo "❌ $api_name: Offline"
        redis-cli -h $REDIS_HOST -p $REDIS_PORT SET "external:${api_name}:status" "offline"
    fi
}

# Verificar APIs principais
check_api_connectivity "coingecko" "https://api.coingecko.com/api/v3/ping"
check_api_connectivity "coinmarketcap" "https://pro-api.coinmarketcap.com/v1/key/info"
check_api_connectivity "newsapi" "https://newsapi.org/v2/sources"
check_api_connectivity "blockchain" "https://api.blockchain.info/stats"

echo "🎯 Monitoramento concluído!"
