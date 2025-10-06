#!/bin/bash
# Script para monitorar e otimizar configurações de auto-scaling

LOG_FILE="scaling-config/autoscaling-monitor.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Monitorar métricas atuais
monitor_current_metrics() {
    log "📊 Monitorando métricas atuais de sistema..."

    # CPU e Memory por serviço
    kubectl top pods -n production | tee -a "$LOG_FILE"

    # Utilização de recursos por nó
    kubectl top nodes | tee -a "$LOG_FILE"

    # Métricas de negócio
    curl -s http://business-intelligence:8086/metrics | grep -E "(revenue|users|transactions)" | tee -a "$LOG_FILE"
}

# Analisar padrões de uso
analyze_usage_patterns() {
    log "🔍 Analisando padrões de uso..."

    # Padrões diários
    echo "Análise de padrões diários:" >> "$LOG_FILE"
    kubectl get hpa -n production -o yaml | grep -A 5 -B 5 "currentReplicas\|targetCPUUtilization" >> "$LOG_FILE"

    # Padrões semanais
    echo "Análise de padrões semanais:" >> "$LOG_FILE"
    kubectl get hpa -n production --sort-by=.status.lastScaleTime >> "$LOG_FILE"
}

# Otimizar configurações de HPA
optimize_hpa_settings() {
    log "⚙️ Otimizando configurações de HPA..."

    # Ajustar thresholds baseado em padrões observados
    kubectl patch hpa sec-ultra-revolutionary-hpa -n production --patch '
    spec:
      metrics:
      - type: Resource
        resource:
          name: cpu
          target:
            type: Utilization
            averageUtilization: 65
      - type: Resource
        resource:
          name: memory
          target:
            type: Utilization
            averageUtilization: 75
    '

    # Atualizar políticas de scaling
    kubectl patch hpa sec-ultra-revolutionary-hpa -n production --patch '
    spec:
      behavior:
        scaleDown:
          stabilizationWindowSeconds: 600
        scaleUp:
          stabilizationWindowSeconds: 60
    '
}

# Ajustar recursos baseado em demanda
adjust_resources() {
    log "🔧 Ajustando recursos baseado em demanda..."

    # Obter métricas atuais
    CURRENT_PODS=$(kubectl get pods -n production --field-selector=status.phase=Running | wc -l)
    CURRENT_CPU=$(kubectl top pods -n production --no-headers | awk '{sum += $2} END {print sum}')

    # Calcular recursos necessários
    RECOMMENDED_PODS=$(( CURRENT_PODS + (CURRENT_PODS * 20 / 100) ))
    RECOMMENDED_CPU=$(( CURRENT_CPU + (CURRENT_CPU * 15 / 100) ))

    log "Pods atuais: $CURRENT_PODS, recomendados: $RECOMMENDED_PODS"
    log "CPU atual: ${CURRENT_CPU}m, recomendado: ${RECOMMENDED_CPU}m"

    # Aplicar ajustes se necessário
    if [ $RECOMMENDED_PODS -gt $CURRENT_PODS ]; then
        kubectl scale deployment sec-ultra-revolutionary -n production --replicas=$RECOMMENDED_PODS
        log "✅ Escalonado para $RECOMMENDED_PODS réplicas"
    fi
}

# Previsão de demanda futura
predict_future_demand() {
    log "🔮 Prevendo demanda futura..."

    # Usar modelo de IA para prever demanda
    DEMAND_PREDICTION=$(curl -s "http://business-intelligence:8086/api/predict-demand?hours=24" | jq -r '.predicted_demand' 2>/dev/null || echo "100")

    # Ajustar capacidade baseada na previsão
    PREDICTED_CAPACITY=$(( DEMAND_PREDICTION * 12 / 10 )) # 20% buffer

    log "Demanda prevista: $DEMAND_PREDICTION, capacidade recomendada: $PREDICTED_CAPACITY"

    # Pré-escalar se demanda prevista for alta
    if [ $PREDICTED_CAPACITY -gt $(kubectl get deployment sec-ultra-revolutionary -n production -o jsonpath='{.spec.replicas}') ]; then
        kubectl scale deployment sec-ultra-revolutionary -n production --replicas=$PREDICTED_CAPACITY
        log "✅ Pré-escalado para $PREDICTED_CAPACITY réplicas baseado em previsão"
    fi
}

# Relatório de eficiência de scaling
generate_scaling_report() {
    log "📋 Gerando relatório de eficiência de scaling..."

    cat > "scaling-config/efficiency-report-$(date +%Y%m%d).md" << EOF
# 🚀 Relatório de Eficiência de Auto-Scaling
## Data: $(date)
## Ambiente: Produção

## Métricas de Performance
- **Tempo médio de scale-up:** $(grep "scale-up" "$LOG_FILE" | tail -5 | awk '{print $3}' | awk '{sum += $1} END {print sum/NR "s"}')
- **Tempo médio de scale-down:** $(grep "scale-down" "$LOG_FILE" | tail -5 | awk '{print $3}' | awk '{sum += $1} END {print sum/NR "s"}')
- **Eficiência de CPU:** $(kubectl top nodes --no-headers | awk '{sum += $3} END {print 100 - (sum/NR) "%"}')
- **Eficiência de memória:** $(kubectl top nodes --no-headers | awk '{sum += $5} END {print 100 - (sum/NR) "%"}')

## Eventos de Scaling (Últimas 24h)
$(kubectl get events --sort-by=.lastTimestamp | grep -i scaling | tail -10)

## Recomendações de Otimização
1. **CPU Threshold:** Considerar redução para 60% se aplicações são CPU-bound
2. **Memory Threshold:** Manter em 80% para estabilidade
3. **Scale-up Speed:** Otimizado para 50% para resposta rápida
4. **Scale-down Delay:** 10 minutos é adequado para evitar flapping

## Custos de Infraestrutura
- **Custo atual:** Estimado baseado em recursos atuais
- **Otimização potencial:** Até 30% com ajustes finos
- **ROI do auto-scaling:** Cálculo baseado em eficiência

## Próximos Passos
1. Implementar machine learning para previsão de demanda
2. Configurar políticas de scaling baseadas em métricas de negócio
3. Integrar com sistemas de monitoramento de custos
4. Otimizar para workloads específicos (blockchain, AI, metaverso)

---
*Relatório gerado automaticamente em:* $(date)
