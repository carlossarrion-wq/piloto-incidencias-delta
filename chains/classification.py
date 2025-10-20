"""
Chain de clasificación de incidencias usando LangChain
"""
import json
import logging
from typing import Dict, Any
from datetime import datetime
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from models.llm_factory import LLMFactory
from prompts.classification import CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)


class CausaAlternativa(BaseModel):
    """Modelo para causas alternativas"""
    causa: str = Field(description="Nombre de la causa alternativa")
    probabilidad: float = Field(description="Probabilidad de esta causa (0.0 a 1.0)")


class ClassificationOutput(BaseModel):
    """Modelo de salida para la clasificación"""
    causa_raiz_predicha: str = Field(description="Causa raíz principal identificada")
    confianza: float = Field(description="Nivel de confianza en la clasificación (0.0 a 1.0)")
    razonamiento: str = Field(description="Explicación detallada del razonamiento")
    keywords_detectadas: list[str] = Field(description="Keywords técnicas detectadas")
    causas_alternativas: list[CausaAlternativa] = Field(description="Causas alternativas posibles")


class ClassificationChain:
    """Chain para clasificar incidencias y determinar causa raíz"""
    
    def __init__(self):
        """Inicializa el chain de clasificación"""
        self.llm = LLMFactory.create_chat_model(temperature=0.0)
        self.parser = PydanticOutputParser(pydantic_object=ClassificationOutput)
        self._setup_chain()
    
    def _setup_chain(self):
        """Configura el chain con los prompts"""
        system_message = SystemMessagePromptTemplate.from_template(
            CLASSIFICATION_SYSTEM_PROMPT
        )
        
        human_message = HumanMessagePromptTemplate.from_template(
            CLASSIFICATION_PROMPT + "\n\n{format_instructions}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            system_message,
            human_message
        ])
        
        logger.info("Chain de clasificación configurado")
    
    def classify(
        self,
        ticket_id: str,
        resumen: str,
        notas: str,
        fecha_creacion: datetime
    ) -> Dict[str, Any]:
        """
        Clasifica una incidencia y determina su causa raíz
        
        Args:
            ticket_id: ID del ticket
            resumen: Resumen de la incidencia
            notas: Notas adicionales
            fecha_creacion: Fecha de creación
            
        Returns:
            Diccionario con la clasificación y metadatos
        """
        try:
            start_time = datetime.now()
            
            # Preparar el prompt
            messages = self.prompt.format_messages(
                ticket_id=ticket_id,
                resumen=resumen,
                notas=notas or "No hay notas adicionales",
                fecha_creacion=fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                format_instructions=self.parser.get_format_instructions()
            )
            
            # Invocar el modelo
            logger.info(f"Clasificando incidencia {ticket_id}")
            response = self.llm.invoke(messages)
            
            # Parsear la respuesta
            try:
                # Intentar parsear como JSON primero
                content = response.content
                if isinstance(content, str):
                    # Limpiar markdown si existe
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    
                    result_dict = json.loads(content)
                else:
                    result_dict = content
                
                # Convertir a formato esperado
                result = {
                    "ticket_id": ticket_id,
                    "causa_raiz_predicha": result_dict.get("causa_raiz_predicha", "Desconocido"),
                    "confianza": float(result_dict.get("confianza", 0.0)),
                    "razonamiento": result_dict.get("razonamiento", ""),
                    "keywords_detectadas": result_dict.get("keywords_detectadas", []),
                    "causas_alternativas": result_dict.get("causas_alternativas", []),
                    "tiempo_procesamiento_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                    "modelo_version": self.llm.model_id
                }
                
                logger.info(f"Incidencia {ticket_id} clasificada: {result['causa_raiz_predicha']} (confianza: {result['confianza']})")
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Error al parsear respuesta JSON: {e}")
                logger.error(f"Contenido recibido: {response.content}")
                
                # Retornar resultado por defecto
                return {
                    "ticket_id": ticket_id,
                    "causa_raiz_predicha": "Error de Procesamiento",
                    "confianza": 0.0,
                    "razonamiento": f"Error al parsear respuesta del modelo: {str(e)}",
                    "keywords_detectadas": [],
                    "causas_alternativas": [],
                    "tiempo_procesamiento_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                    "modelo_version": self.llm.model_id
                }
                
        except Exception as e:
            logger.error(f"Error al clasificar incidencia {ticket_id}: {e}")
            raise
    
    def classify_batch(
        self,
        incidents: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Clasifica un lote de incidencias
        
        Args:
            incidents: Lista de diccionarios con datos de incidencias
            
        Returns:
            Lista de resultados de clasificación
        """
        results = []
        
        for incident in incidents:
            try:
                result = self.classify(
                    ticket_id=incident.get("ticket_id", ""),
                    resumen=incident.get("resumen", ""),
                    notas=incident.get("notas", ""),
                    fecha_creacion=incident.get("fecha_creacion", datetime.now())
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error al procesar incidencia {incident.get('ticket_id')}: {e}")
                results.append({
                    "ticket_id": incident.get("ticket_id", ""),
                    "causa_raiz_predicha": "Error",
                    "confianza": 0.0,
                    "razonamiento": f"Error: {str(e)}",
                    "keywords_detectadas": [],
                    "causas_alternativas": [],
                    "tiempo_procesamiento_ms": 0,
                    "modelo_version": "error"
                })
        
        return results
