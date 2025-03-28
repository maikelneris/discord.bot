import os
import logging
import requests
from abc import ABC, abstractmethod
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> dict:
        pass

    @abstractmethod
    def format_response(self, results: dict) -> tuple[str, str]:
        pass

class GoogleSearchProvider(SearchProvider):
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.cse_id = os.getenv('GOOGLE_CSE_ID')
        self.language = os.getenv('DEFAULT_LANGUAGE', 'pt-BR')
        self.region = os.getenv('DEFAULT_REGION', 'br')
        self.country = os.getenv('DEFAULT_COUNTRY', 'BR')

    def search(self, query: str) -> dict:
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': 3,
                'lr': f'lang_{self.language}',
                'gl': self.region,
                'cr': self.country
            }
            
            logging.debug(f"Search parameters: {params}")
            response = requests.get(url, params=params)
            logging.debug(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logging.error(f"Google API error: {response.text}")
                raise Exception(f"Google API error: {response.status_code}")
            
            data = response.json()
            logging.debug(f"Response data: {data}")
            
            if 'items' not in data:
                logging.warning("No search results found")
                return {'error': 'No results found'}
            
            return data
            
        except Exception as e:
            logging.error(f"Error in Google search: {str(e)}")
            return {'error': str(e)}

    def format_response(self, results: dict) -> tuple[str, str]:
        if 'error' in results:
            return "Desculpe, não consegui encontrar informações sobre isso.", "Desculpe, não consegui encontrar informações sobre isso."

        items = results.get('items', [])
        if not items:
            return "Desculpe, não consegui encontrar informações sobre isso.", "Desculpe, não consegui encontrar informações sobre isso."

        # Format text response
        response_parts = []
        for i, item in enumerate(items, 1):
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            response_parts.append(f"{i}. {snippet}\nFonte: {link}\n")

        text_response = "\n".join(response_parts)

        # Get first sentence for voice response
        first_snippet = items[0].get('snippet', '')
        voice_response = first_snippet.split('.')[0] + '.' if '.' in first_snippet else first_snippet[:15] + '...'

        return text_response, voice_response

class BloomzSearchProvider(SearchProvider):
    def __init__(self):
        self.model_name = os.getenv('AI_MODEL', 'bigscience/bloomz-7b1')
        self.max_length = int(os.getenv('AI_MAX_LENGTH', '150'))
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logging.info(f"Loading BLOOMZ model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto"
        )
        logging.info("BLOOMZ model loaded successfully")

    def search(self, query: str) -> dict:
        try:
            # Create prompt in Portuguese
            prompt = f"Pergunta: {query}\nResposta:"
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs,
                max_length=self.max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the answer part
            response = response.split("Resposta:")[-1].strip()
            
            return {'response': response}
            
        except Exception as e:
            logging.error(f"Error in BLOOMZ search: {str(e)}")
            return {'error': str(e)}

    def format_response(self, results: dict) -> tuple[str, str]:
        if 'error' in results:
            return "Desculpe, não consegui gerar uma resposta.", "Desculpe, não consegui gerar uma resposta."

        response = results.get('response', '')
        if not response:
            return "Desculpe, não consegui gerar uma resposta.", "Desculpe, não consegui gerar uma resposta."

        # Get first sentence for voice response
        voice_response = response.split('.')[0] + '.' if '.' in response else response[:15] + '...'

        return response, voice_response

class SearchProviderFactory:
    def __init__(self):
        self.google_provider = GoogleSearchProvider()
        self.ai_provider = None  # Lazy initialization
        logging.info("SearchProviderFactory initialized with Google provider")

    def get_provider(self, mode: str) -> SearchProvider:
        if mode == 'google':
            return self.google_provider
        elif mode == 'ai':
            if self.ai_provider is None:
                logging.info("Initializing AI provider (BLOOMZ)")
                self.ai_provider = BloomzSearchProvider()
            return self.ai_provider
        else:
            raise ValueError(f"Invalid search mode: {mode}") 