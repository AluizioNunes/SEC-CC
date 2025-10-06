#!/bin/bash
# Script para sincronizar dados externos

echo "🔄 Iniciando sincronização de dados externos..."

# Configurações
REDIS_HOST=${REDIS_HOST:-localhost}
REDIS_PORT=${REDIS_PORT:-6379}
LOG_FILE="external-integrations/sync.log"

# Função para log
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Função para sincronizar dados do CoinGecko
sync_coingecko() {
    log "🔗 Sincronizando dados do CoinGecko..."
    
    # Obter preços de criptomoedas
    curl -s "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false" | \
    jq '.[] | {symbol: .symbol, price: .current_price, volume: .total_volume, market_cap: .market_cap}' | \
    redis-cli -h $REDIS_HOST -p $REDIS_PORT -x SET "external:coingecko:prices:$(date +%s)" < /dev/stdin
    
    log "✅ Dados do CoinGecko sincronizados!"
}

# Função para sincronizar dados de notícias
sync_news() {
    log "📰 Sincronizando notícias..."
    
    # Exemplo de sincronização de notícias sobre cripto
    curl -s "https://newsapi.org/v2/everything?q=cryptocurrency&apiKey=YOUR_NEWS_API_KEY&sortBy=publishedAt&pageSize=50" | \
    jq '.articles[] | {title: .title, description: .description, url: .url, publishedAt: .publishedAt}' | \
    redis-cli -h $REDIS_HOST -p $REDIS_PORT -x SET "external:news:crypto:$(date +%s)" < /dev/stdin
    
    log "✅ Notícias sincronizadas!"
}

# Função para sincronizar dados sociais
sync_social() {
    log "📱 Sincronizando dados sociais..."
    
    # Exemplo de sincronização de tweets sobre cripto
    curl -s "https://api.twitter.com/2/tweets/search/recent?query=cryptocurrency&max_results=50" \
    -H "Authorization: Bearer YOUR_TWITTER_BEARER_TOKEN" | \
    jq '.data[] | {text: .text, author_id: .author_id, created_at: .created_at}' | \
    redis-cli -h $REDIS_HOST -p $REDIS_PORT -x SET "external:social:twitter:$(date +%s)" < /dev/stdin
    
    log "✅ Dados sociais sincronizados!"
}

# Função para sincronizar dados de blockchain
sync_blockchain() {
    log "⛓️ Sincronizando dados de blockchain..."
    
    # Obter estatísticas da rede Bitcoin
    curl -s "https://api.blockchain.info/stats" | \
    jq '{market_price_usd: .market_price_usd, hash_rate: .hash_rate, total_bc: .total_bc}' | \
    redis-cli -h $REDIS_HOST -p $REDIS_PORT -x SET "external:blockchain:bitcoin:$(date +%s)" < /dev/stdin
    
    log "✅ Dados de blockchain sincronizados!"
}

# Executar sincronizações
sync_coingecko
sync_news
sync_social
sync_blockchain

log "🎉 Sincronização de dados externos concluída!"

# Agendar próxima sincronização (a cada 5 minutos)
echo "⏰ Agendando próxima sincronização em 5 minutos..."
