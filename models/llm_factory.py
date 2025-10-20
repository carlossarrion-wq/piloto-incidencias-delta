"""
Factory para crear instancias de modelos LLM de AWS Bedrock
"""
import logging
from typing import Optional
from langchain_aws import ChatBedrock
from langchain_community.embeddings import BedrockEmbeddings
from config import config

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory para crear y gestionar modelos LLM"""
    
    @staticmethod
    def create_chat_model(
        model_id: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> ChatBedrock:
        """
        Crea una instancia de ChatBedrock para Claude 3 Haiku
        
        Args:
            model_id: ID del modelo (por defecto usa config)
            temperature: Temperatura para generación (0.0 = determinista)
            max_tokens: Máximo de tokens a generar
            
        Returns:
            Instancia de ChatBedrock configurada
        """
        model = model_id or config.BEDROCK_MODEL_ID
        
        try:
            llm = ChatBedrock(
                model_id=model,
                region_name=config.AWS_REGION,
                model_kwargs={
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            )
            logger.info(f"Modelo de chat creado: {model}")
            return llm
        except Exception as e:
            logger.error(f"Error al crear modelo de chat: {e}")
            raise
    
    @staticmethod
    def create_embedding_model(
        model_id: Optional[str] = None
    ) -> BedrockEmbeddings:
        """
        Crea una instancia de BedrockEmbeddings para Titan
        
        Args:
            model_id: ID del modelo de embeddings (por defecto usa config)
            
        Returns:
            Instancia de BedrockEmbeddings configurada
        """
        model = model_id or config.BEDROCK_EMBEDDING_MODEL_ID
        
        try:
            embeddings = BedrockEmbeddings(
                model_id=model,
                region_name=config.AWS_REGION
            )
            logger.info(f"Modelo de embeddings creado: {model}")
            return embeddings
        except Exception as e:
            logger.error(f"Error al crear modelo de embeddings: {e}")
            raise
