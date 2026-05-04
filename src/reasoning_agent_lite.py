"""
Reasoning Agent Lite - Versión simplificada para Sprint 3

Usa sklearn para clasificación de alertas sin dependencias pesadas (no torch).
Alternativa rápida y funcional para demostración.
"""

import logging
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os

logger = logging.getLogger(__name__)


class ReasoningAgentLite:
    """
    Agente de razonamiento ligero usando ML clásico (sklearn).
    Clasifica alertas sin requerir torch ni modelos grandes.
    """

    def __init__(self):
        """Inicializa el agente con modelo pre-entrenado simple."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Entrenar modelo simple con ejemplos conocidos
        self._initialize_model()
        
        # Palabras clave y contexto
        self.critical_keywords = {
            "huelga", "paro", "cierre", "suspensión", "bloqueado", "bloqueo",
            "cortado", "vía cortada", "carretera cerrada", "evacuación", "peligro",
            "urgente", "alerta", "tormenta", "lluvia extrema", "derrumbe",
            "inundación", "avalancha", "protesta", "manifestación"
        }
        
        self.tourism_locations = {
            "machu picchu", "ollantaytambo", "cusco", "valle sagrado",
            "plaza de armas", "inca trail", "sacsayhuamán", "aguas calientes",
            "cusco airport", "perurail", "incarail", "tren"
        }
        
        self.logger.info("✅ Agente de Razonamiento Ligero inicializado")

    def _initialize_model(self):
        """Inicializa modelo con datos de entrenamiento simple."""
        # Ejemplos de entrenamiento
        textos_criticos = [
            "PeruRail suspende trenes por huelga indefinida",
            "Vía cerrada por derrumbe en ruta a Machu Picchu",
            "Bloqueo de carreteras en Cusco por protesta",
            "Evacuación de turistas por lluvia extrema",
            "Cierre de Machu Picchu por peligro",
            "Huelga de transporte en Ollantaytambo"
        ]
        
        textos_informativos = [
            "Inti Raymi 2026 80% vendido",
            "Nuevas rutas de senderismo abiertas",
            "Museo de Cusco abre nueva ala",
            "Festival de música en Plaza de Armas",
            "Cambios de horario en PeruRail",
            "Entrada a Machu Picchu con descuento"
        ]
        
        textos_irrelevantes = [
            "Noticias del fútbol europeo",
            "Bolsa de valores sube 2%",
            "Película nueva en cines",
            "Receta de comida italiana",
            "Tecnología del iPhone 15"
        ]
        
        # Combinar datos
        textos = textos_criticos + textos_informativos + textos_irrelevantes
        etiquetas = [0]*len(textos_criticos) + [1]*len(textos_informativos) + [2]*len(textos_irrelevantes)
        
        # Entrenar vectorizador y clasificador
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        X = self.vectorizer.fit_transform(textos)
        
        self.classifier = MultinomialNB()
        self.classifier.fit(X, etiquetas)
        
        self.label_map = {0: "CRÍTICA", 1: "INFORMATIVA", 2: "IRRELEVANTE"}

    def classify_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Clasifica una alerta individual."""
        try:
            # Combinar texto
            titulo = alert.get('titulo', '').lower()
            descripcion = alert.get('descripcion', alert.get('enlace', '')).lower()
            texto_completo = f"{titulo} {descripcion}"
            
            # Detectar ubicaciones
            ubicaciones = self._detect_locations(texto_completo)
            
            # Verificar palabras clave críticas
            tiene_critica_keyword = any(kw in texto_completo for kw in self.critical_keywords)
            
            # Clasificar
            X = self.vectorizer.transform([texto_completo])
            prediccion = self.classifier.predict(X)[0]
            probabilidades = self.classifier.predict_proba(X)[0]
            confianza = int(max(probabilidades) * 100)
            
            clasificacion = self.label_map[prediccion]
            
            # Booster para palabras clave críticas
            if tiene_critica_keyword and ubicaciones:
                if confianza < 70:
                    clasificacion = "CRÍTICA"
                    confianza = min(95, confianza + 20)
            
            # Detectar tipo de evento
            tipo_evento = self._detect_event_type(texto_completo)
            
            # Generar recomendación
            recomendacion = self._generate_recommendation(clasificacion, ubicaciones, tipo_evento)
            
            return {
                "id": alert.get('id'),
                "titulo": alert.get('titulo', 'Sin título'),
                "fuente": alert.get('fuente', 'Desconocida'),
                "enlace": alert.get('enlace', ''),
                "clasificacion": clasificacion,
                "confianza": confianza,
                "ubicaciones": ubicaciones,
                "tipo_evento": tipo_evento,
                "resumen_ia": self._generate_summary(titulo, clasificacion),
                "recomendacion": recomendacion,
                "fecha_scrape": alert.get('fecha_scrape', ''),
                "fuente_original": alert.get('fuente', ''),
                "tipo": alert.get('tipo', 'alerta'),
                "score_urgencia": self._calculate_urgency_score(clasificacion, confianza)
            }
        
        except Exception as e:
            self.logger.error(f"Error clasificando alerta: {e}")
            return {
                "id": alert.get('id'),
                "titulo": alert.get('titulo', ''),
                "fuente": alert.get('fuente', ''),
                "clasificacion": "INFORMATIVA",
                "confianza": 50,
                "error": str(e)
            }

    def classify_batch(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clasifica múltiples alertas."""
        self.logger.info(f"🔄 Clasificando {len(alerts)} alertas...")
        
        clasificadas = []
        for i, alert in enumerate(alerts):
            try:
                result = self.classify_alert(alert)
                clasificadas.append(result)
                
                if (i + 1) % 5 == 0:
                    self.logger.info(f"   ✅ {i + 1}/{len(alerts)} procesadas")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Error en alerta {i+1}: {e}")
                continue
        
        self.logger.info(f"✅ Clasificación completada: {len(clasificadas)} alertas procesadas")
        return clasificadas

    def _detect_locations(self, texto: str) -> List[str]:
        """Detecta ubicaciones turísticas."""
        ubicaciones_encontradas = []
        for loc in self.tourism_locations:
            if loc in texto:
                ubicaciones_encontradas.append(loc.title())
        return list(set(ubicaciones_encontradas))

    def _detect_event_type(self, texto: str) -> str:
        """Detecta tipo de evento."""
        if any(kw in texto for kw in ["huelga", "paro", "protesta"]):
            return "protesta_social"
        elif any(kw in texto for kw in ["cierre", "suspensión", "bloqueado"]):
            return "cierre_transporte"
        elif any(kw in texto for kw in ["lluvia", "tormenta", "nieve", "derrumbe"]):
            return "fenomeno_natural"
        elif any(kw in texto for kw in ["evento", "festival", "inti raymi"]):
            return "evento_cultural"
        elif any(kw in texto for kw in ["restricción", "entrada", "ticket"]):
            return "restriccion_acceso"
        else:
            return "otro"

    def _generate_summary(self, titulo: str, clasificacion: str) -> str:
        """Genera resumen contextual."""
        if clasificacion == "CRÍTICA":
            return f"⚠️ ALERTA CRÍTICA: {titulo[:80]}"
        elif clasificacion == "INFORMATIVA":
            return f"ℹ️ Información: {titulo[:80]}"
        else:
            return titulo[:80]

    def _generate_recommendation(self, clasificacion: str, ubicaciones: List[str], tipo_evento: str) -> str:
        """Genera recomendación para agencia."""
        if clasificacion == "CRÍTICA":
            if ubicaciones:
                return f"Notificar INMEDIATAMENTE a turistas en {', '.join(ubicaciones)}"
            else:
                return "Notificar INMEDIATAMENTE a todos los turistas activos"
        elif clasificacion == "INFORMATIVA":
            return "Compartir como información general con turistas interesados"
        else:
            return "No requiere notificación"

    def _calculate_urgency_score(self, clasificacion: str, confianza: int) -> int:
        """Calcula score de urgencia."""
        scores = {
            "CRÍTICA": 90,
            "INFORMATIVA": 50,
            "IRRELEVANTE": 10
        }
        base_score = scores.get(clasificacion, 50)
        adjusted_score = int(base_score * (confianza / 100))
        return min(100, adjusted_score)


class ReasoningPipelineLite:
    """Pipeline simplificado sin torch."""
    
    def __init__(self, data_path: str = './data'):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.data_path = data_path
        self.reasoning_agent = ReasoningAgentLite()
    
    def process_raw_alerts(self, raw_alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa alertas raw."""
        self.logger.info("\n" + "="*60)
        self.logger.info("🧠 ETAPA 2: RAZONAMIENTO (Motor IA Local - Lite)")
        self.logger.info("="*60)
        
        # Enriquecer alertas
        for i, alert in enumerate(raw_alerts):
            if 'id' not in alert:
                alert['id'] = i + 1
        
        # Clasificar
        classified_alerts = self.reasoning_agent.classify_batch(raw_alerts)
        
        # Estadísticas
        stats = self._calculate_stats(classified_alerts)
        self.logger.info(f"\n📊 Estadísticas de Clasificación:")
        self.logger.info(f"   CRÍTICA: {stats['critica']} ({stats['critica_pct']:.1f}%)")
        self.logger.info(f"   INFORMATIVA: {stats['informativa']} ({stats['informativa_pct']:.1f}%)")
        self.logger.info(f"   IRRELEVANTE: {stats['irrelevante']} ({stats['irrelevante_pct']:.1f}%)")
        
        return classified_alerts
    
    def _calculate_stats(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula estadísticas."""
        total = len(alerts)
        critica = sum(1 for a in alerts if a.get('clasificacion') == 'CRÍTICA')
        informativa = sum(1 for a in alerts if a.get('clasificacion') == 'INFORMATIVA')
        irrelevante = sum(1 for a in alerts if a.get('clasificacion') == 'IRRELEVANTE')
        
        return {
            'critica': critica,
            'informativa': informativa,
            'irrelevante': irrelevante,
            'critica_pct': (critica / total * 100) if total > 0 else 0,
            'informativa_pct': (informativa / total * 100) if total > 0 else 0,
            'irrelevante_pct': (irrelevante / total * 100) if total > 0 else 0
        }
