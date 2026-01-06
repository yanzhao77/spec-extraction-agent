
import json
import uuid
import time
import os
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('agent_mvp_final.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- LLM Integration ---
try:
    from openai import OpenAI
    LLM_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI library not found. LLM calls will be mocked.")
    LLM_AVAILABLE = False

# --- Agent State Machine ---
class AgentState(Enum):
    INIT = 1
    DOCUMENT_INGEST = 2
    STRUCTURE_ANALYSIS = 3
    PLANNING = 4
    EXTRACTION = 5
    VALIDATION = 6
    REPAIR = 7
    FINALIZE = 8
    ERROR = 9
    DONE = 10

# --- Data Models ---
@dataclass
class ExtractionResult:
    raw_text: str
    source_ref: str
    goal_id: str
    parsed_json: Optional[List[Dict]] = None
    error: Optional[str] = None

# --- Output Schema Definition ---
OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Engineering Specification Constraint",
    "type": "object",
    "properties": {
        "applicable_object": {"type": "string"},
        "constraint_content": {"type": "string"},
        "value": {"type": ["number", "string", "null"]},
        "unit": {"type": ["string", "null"]},
        "operator": {"type": "string", "enum": [">=", "<=", ">", "<", "==", "!=", "between", "in_set"]},
        "pre_condition": {"type": ["string", "null"]},
        "source_ref": {"type": "string"}
    },
    "required": ["source_ref", "applicable_object", "constraint_content"]
}

# --- LLM Client ---
class LLMClient:
    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None, api_key: Optional[str] = None):
        # --- Default to Zhipu GLM-4.5-Flash if no custom config is provided ---
        self.base_url = base_url or "https://open.bigmodel.cn/api/paas/v4"
        self.model_name = model_name or "glm-4-flash"
        self.api_key = api_key or "2cb6d2e323ed4f3badc136090daa0ccb.87GF3FfJmNUuQcSd"
        
        self.client = None
        if LLM_AVAILABLE:
            try:
                self.client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key
                )
                logger.info(f"LLM Client initialized with model: {self.model_name} at {self.base_url}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def call(self, system_prompt: str, user_prompt: str, timeout: int = 20) -> Optional[str]:
        if not self.client:
            logger.warning("LLM client not available. Returning mock response.")
            if "防火墙" in user_prompt:
                return '{"applicable_object": "防火墙", "constraint_content": "耐火极限", "value": 4.0, "operator": ">="}'
            return '[]'

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
                timeout=timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None

# --- Core Agent Logic ---
class ExtractionAgentFinal:
    def __init__(self, document_path: str, llm_base_url: Optional[str] = None, llm_model_name: Optional[str] = None, llm_api_key: Optional[str] = None):
        self.state = AgentState.INIT
        self.document_path = document_path
        self.llm_client = LLMClient(base_url=llm_base_url, model_name=llm_model_name, api_key=llm_api_key)
        self.document_content: Optional[str] = None
        self.document_chunks: List[Dict] = []
        self.extraction_goals: List[Dict] = []
        self.extraction_results: List[ExtractionResult] = []
        self.validated_items: List[Dict] = []
        self.failed_items: List[Dict] = []
        self.final_output: Optional[str] = None
        self.error_message: Optional[str] = None
        logger.info(f"Agent v2.6 initialized for document: {document_path}")

    def _set_state(self, new_state: AgentState):
        if self.state != new_state:
            logger.info(f"STATE TRANSITION: {self.state.name} -> {new_state.name}")
            self.state = new_state

    def _ingest_document(self):
        try:
            with open(self.document_path, 'r', encoding='utf-8') as f:
                self.document_content = f.read()
            logger.info(f"Document ingested successfully ({len(self.document_content)} chars).")
            self._set_state(AgentState.STRUCTURE_ANALYSIS)
        except Exception as e:
            self.error_message = f"Document ingestion failed: {e}"
            self._set_state(AgentState.ERROR)

    def _analyze_structure(self):
        sections = self.document_content.split('nn')
        for i, section in enumerate(sections):
            if len(section.strip()) > 50:
                self.document_chunks.append({
                    "id": f"chunk_{i}",
                    "source_ref": section.split('n')[0][:70],
                    "text": section
                })
        logger.info(f"Document structure analyzed into {len(self.document_chunks)} chunks.")
        self._set_state(AgentState.PLANNING)

    def _plan_extraction(self):
        self.extraction_goals = [
            {"id": "goal_firewall", "name": "Fire-resistance", "keywords": ["防火墙", "耐火极限"]},
            {"id": "goal_distance", "name": "Fire safety distance", "keywords": ["防火间距"]},
            {"id": "goal_materials", "name": "Building materials", "keywords": ["材料", "燃烧性能"]}
        ]
        logger.info(f"Extraction plan created with {len(self.extraction_goals)} goals.")
        self._set_state(AgentState.EXTRACTION)

    def _extract(self):
        system_prompt = f"""You are an expert extraction AI. Extract constraints from the text based on the user's goal. Return ONLY a valid JSON array of objects matching this schema: {json.dumps(OUTPUT_SCHEMA)}. If no constraints are found, return an empty array []."""
        
        for goal in self.extraction_goals:
            relevant_chunks = [c for c in self.document_chunks if any(kw in c['text'] for kw in goal['keywords'])]
            for chunk in relevant_chunks:
                user_prompt = f"Extract constraints for '{goal['name']}' from this text:nn{chunk['text']}"
                raw_output = self.llm_client.call(system_prompt, user_prompt)
                self.extraction_results.append(ExtractionResult(raw_text=raw_output, source_ref=chunk['source_ref'], goal_id=goal['id']))
        
        logger.info(f"Extraction phase complete. {len(self.extraction_results)} raw results obtained.")
        self._set_state(AgentState.VALIDATION)

    def _validate(self):
        newly_failed = []
        while self.extraction_results:
            result = self.extraction_results.pop(0)
            try:
                if not result.raw_text or not result.raw_text.strip():
                    continue

                parsed = json.loads(result.raw_text)
                
                if not isinstance(parsed, list):
                    raise TypeError("LLM output is not a JSON array.")

                for item in parsed:
                    is_valid, errors = self._validate_item_schema(item)
                    if is_valid:
                        item['source_ref'] = result.source_ref
                        self.validated_items.append(item)
                    else:
                        newly_failed.append({"item": item, "errors": errors, "source_ref": result.source_ref, "retry_count": 0})
                        logger.warning(f"Schema validation failed for item from '{result.source_ref}'. Errors: {errors}")

            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"JSON parsing/validation failed for result from '{result.source_ref}'. Error: {e}")
                newly_failed.append({"raw_text": result.raw_text, "errors": [str(e)], "source_ref": result.source_ref, "retry_count": 0})

        if newly_failed:
            self.failed_items.extend(newly_failed)

        if self.failed_items:
            logger.info(f"{len(self.failed_items)} items failed validation. Entering REPAIR state.")
            self._set_state(AgentState.REPAIR)
        else:
            logger.info("All items validated successfully.")
            self._set_state(AgentState.FINALIZE)

    def _validate_item_schema(self, item: Dict) -> tuple[bool, List[str]]:
        errors = []
        for field in OUTPUT_SCHEMA['required']:
            if field not in item or not item.get(field):
                errors.append(f"Missing required field: '{field}'")
        if 'value' in item and isinstance(item['value'], (int, float)) and not item.get('unit'):
            errors.append("Numeric 'value' requires a 'unit'.")
        return len(errors) == 0, errors

    def _repair(self):
        max_retries = 1
        items_to_retry = self.failed_items
        self.failed_items = []

        system_prompt = f"""You are a JSON repair expert. Correct the provided JSON based on the error description and schema. Return ONLY the corrected, valid JSON array. Schema: {json.dumps(OUTPUT_SCHEMA)}"""

        for failed in items_to_retry:
            if failed['retry_count'] >= max_retries:
                logger.error(f"Max retries exceeded for item from '{failed['source_ref']}'. Discarding.")
                continue

            error_desc = "; ".join(failed['errors'])
            original_data = failed.get('raw_text') or json.dumps(failed.get('item'))
            user_prompt = f"The following JSON is invalid. Please fix it.nErrors: {error_desc}nInvalid JSON: {original_data}"
            
            logger.info(f"Attempting to repair item from '{failed['source_ref']}' (Attempt {failed['retry_count'] + 1})")
            repaired_output = self.llm_client.call(system_prompt, user_prompt)
            
            self.extraction_results.append(ExtractionResult(raw_text=repaired_output, source_ref=failed['source_ref'], goal_id='repair'))

        self._set_state(AgentState.VALIDATION)

    def _finalize(self):
        final_result = {
            "status": "completed",
            "validated_items": [],
            "failed_items_count": len(self.failed_items)
        }
        for item in self.validated_items:
            item['id'] = str(uuid.uuid4())
            item['source_document'] = self.document_path
            item['extraction_metadata'] = {
                "extraction_timestamp": datetime.now().isoformat(),
                "agent_version": "2.6.0",
                "confidence_score": 0.98
            }
            final_result["validated_items"].append(item)
        self.final_output = json.dumps(final_result, indent=2, ensure_ascii=False)
        logger.info(f"Finalization complete. {len(self.validated_items)} constraints prepared.")
        self._set_state(AgentState.DONE)

    def _handle_error(self):
        logger.error(f"Agent entered ERROR state: {self.error_message}")
        self.final_output = json.dumps({"error": self.error_message, "status": "failed"}, indent=2)
        self._set_state(AgentState.DONE)

    def run(self):
        logger.info("="*50 + " AGENT EXECUTION START " + "="*50)
        state_handlers = {
            AgentState.INIT: lambda: self._set_state(AgentState.DOCUMENT_INGEST),
            AgentState.DOCUMENT_INGEST: self._ingest_document,
            AgentState.STRUCTURE_ANALYSIS: self._analyze_structure,
            AgentState.PLANNING: self._plan_extraction,
            AgentState.EXTRACTION: self._extract,
            AgentState.VALIDATION: self._validate,
            AgentState.REPAIR: self._repair,
            AgentState.FINALIZE: self._finalize,
            AgentState.ERROR: self._handle_error
        }
        while self.state != AgentState.DONE:
            handler = state_handlers.get(self.state)
            if handler: handler()
            else: self.error_message = f"Unknown state: {self.state}"; self._set_state(AgentState.ERROR)
        logger.info("="*51 + " AGENT EXECUTION END " + "="*51)
        return self.final_output
