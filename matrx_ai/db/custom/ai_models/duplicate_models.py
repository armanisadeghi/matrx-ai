from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from matrx_utils import clear_terminal, print_link, to_matrx_json, vcprint

from matrx_ai.db import _setup

_setup()

from matrx_ai.db.custom.ai_models.ai_model_manager import AiModelManager, ai_model_manager_instance
from matrx_ai.db.models import AiModel

ai_model_manager: AiModelManager = ai_model_manager_instance


@dataclass
class ModelCapabilities:
    tuning: bool | None = None
    caching: bool | None = None
    live_api: bool | None = None
    thinking: bool | None = None
    code_execution: bool | None = None
    native_tool_use: bool | None = None
    audio_generation: bool | None = None
    function_calling: bool | None = None
    image_generation: bool | None = None
    search_grounding: bool | None = None
    structured_outputs: bool | None = None
    google_maps_grounding: bool | None = None

    @classmethod
    def from_dict(cls, source: dict[str, Any], overrides: dict[str, Any] | None = None) -> ModelCapabilities:
        overrides = overrides or {}
        return cls(**{k: overrides.get(k, source.get(k)) for k in cls.__dataclass_fields__})

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ModelControls:
    tools: dict[str, Any] | None = None
    stream: dict[str, Any] | None = None
    file_urls: dict[str, Any] | None = None
    image_urls: dict[str, Any] | None = None
    temperature: dict[str, Any] | None = None
    output_format: dict[str, Any] | None = None
    youtube_videos: dict[str, Any] | None = None
    reasoning_effort: dict[str, Any] | None = None
    max_output_tokens: dict[str, Any] | None = None
    reasoning_summary: dict[str, Any] | None = None
    internal_web_search: dict[str, Any] | None = None
    internal_url_context: dict[str, Any] | None = None
    # extended controls discovered from full model audit
    aspect_ratio: dict[str, Any] | None = None
    disable_safety_checker: dict[str, Any] | None = None
    fps: dict[str, Any] | None = None
    frame_images: dict[str, Any] | None = None
    guidance_scale: dict[str, Any] | None = None
    height: dict[str, Any] | None = None
    image_loras: dict[str, Any] | None = None
    image_size: dict[str, Any] | None = None
    include: dict[str, Any] | None = None
    include_thoughts: dict[str, Any] | None = None
    max_completion_tokens: dict[str, Any] | None = None
    max_tokens: dict[str, Any] | None = None
    n: dict[str, Any] | None = None
    negative_prompt: dict[str, Any] | None = None
    output_quality: dict[str, Any] | None = None
    parallel_tool_calls: dict[str, Any] | None = None
    reasoning: dict[str, Any] | None = None
    reference_images: dict[str, Any] | None = None
    response_format: dict[str, Any] | None = None
    seconds: dict[str, Any] | None = None
    seed: dict[str, Any] | None = None
    steps: dict[str, Any] | None = None
    stop_sequences: dict[str, Any] | None = None
    store: dict[str, Any] | None = None
    text: dict[str, Any] | None = None
    thinking_budget: dict[str, Any] | None = None
    tool_choice: dict[str, Any] | None = None
    top_k: dict[str, Any] | None = None
    top_p: dict[str, Any] | None = None
    verbosity: dict[str, Any] | None = None
    width: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, source: dict[str, Any], overrides: dict[str, Any] | None = None) -> ModelControls:
        overrides = overrides or {}
        return cls(**{k: overrides.get(k, source.get(k)) for k in cls.__dataclass_fields__})

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ModelData:
    name: str | None = None
    common_name: str | None = None
    model_class: str | None = None
    provider: str | None = None
    endpoints: list[str] | None = None
    context_window: int | None = None
    max_tokens: int | None = None
    capabilities: dict[str, Any] | list[str] | None = None
    controls: dict[str, Any] | None = None
    model_provider: str | None = None
    is_deprecated: bool | None = None
    is_primary: bool | None = None
    is_premium: bool | None = None
    api_class: str | None = None

    @classmethod
    def from_dict(cls, source: dict[str, Any], overrides: dict[str, Any] | None = None) -> ModelData:
        overrides = overrides or {}
        data: dict[str, Any] = {}
        for k in cls.__dataclass_fields__:
            if k == "capabilities":
                source_caps = source.get("capabilities")
                override_caps = overrides.get("capabilities")
                if isinstance(source_caps, dict):
                    data[k] = ModelCapabilities.from_dict(source_caps, override_caps or {}).to_dict()
                else:
                    data[k] = override_caps if override_caps is not None else source_caps
            elif k == "controls":
                source_ctrls = source.get("controls") or {}
                override_ctrls = overrides.get("controls") or {}
                resolved = ModelControls.from_dict(source_ctrls, override_ctrls).to_dict()
                data[k] = resolved if resolved else None
            else:
                data[k] = overrides.get(k, source.get(k))
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


def audit_dataclass_coverage() -> None:
    local_models_file = Path(__file__).parent / "local_models.json"
    with open(local_models_file, encoding="utf-8") as f:
        all_models: list[dict[str, Any]] = json.load(f)

    known_model_data = set(ModelData.__dataclass_fields__)
    known_capabilities = set(ModelCapabilities.__dataclass_fields__)
    known_controls = set(ModelControls.__dataclass_fields__)

    found_model_data: set[str] = set()
    found_capabilities: set[str] = set()
    found_controls: set[str] = set()

    for model in all_models:
        found_model_data.update(k for k in model if k not in ("id", "dto"))
        caps = model.get("capabilities")
        if isinstance(caps, dict):
            found_capabilities.update(caps)
        ctrls = model.get("controls")
        if isinstance(ctrls, dict):
            found_controls.update(ctrls)

    all_keys = {
        "ModelData": sorted(found_model_data),
        "ModelCapabilities": sorted(found_capabilities),
        "ModelControls": sorted(found_controls),
    }
    missing = {
        "ModelData": sorted(found_model_data - known_model_data),
        "ModelCapabilities": sorted(found_capabilities - known_capabilities),
        "ModelControls": sorted(found_controls - known_controls),
    }

    all_keys_file = Path(__file__).parent / "all_model_keys.json"
    with open(all_keys_file, "w", encoding="utf-8") as f:
        json.dump(all_keys, f, indent=4)
    vcprint(f"[Audit] All discovered keys saved to: {all_keys_file}", color="blue")
    print_link(all_keys_file)

    has_missing = any(missing.values())
    if has_missing:
        gap_file = Path(__file__).parent / "dataclass_gaps.json"
        with open(gap_file, "w", encoding="utf-8") as f:
            json.dump(missing, f, indent=4)
        vcprint(missing, "[Audit] Gaps found — written to dataclass_gaps.json", color="red")
        print_link(gap_file)
    else:
        vcprint("[Audit] All dataclasses fully covered — no missing keys.", color="green")


def save_results(all_models: list[AiModel]):
    output_file = Path(__file__).parent / "local_models.json"
    serializable_result = to_matrx_json(all_models)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_result, f, indent=4)
    vcprint(f"\nLocal models saved to: {output_file}", color="blue")
    print_link(output_file)


async def save_all_models():
    all_models = await ai_model_manager.load_all_models()
    save_results(all_models)
    audit_dataclass_coverage()
    return all_models


async def duplicate_ai_model(model_id_or_name: str, overrides: dict[str, Any]) -> AiModel:
    model = await ai_model_manager.load_model(model_id_or_name)
    vcprint(model, "[Duplicator] Original Model", color="yellow")
    if model:
        model_data = ModelData.from_dict(model.to_dict(), overrides)
    else:
        vcprint(f"[Duplicator] Model not found: {model_id_or_name}", color="red")
        return None
    
    
    new_model = await ai_model_manager.create_ai_model(**model_data.to_dict())
    vcprint(new_model, "[Duplicator] New model", color="blue")
    return model_data

"""
Tasks:
- [X] gemini-3-flash-preview	$0.50/M	$3.00/M	Flat
- [X] gemini-3.1-flash-lite-preview	$0.25/M (text/img/video)	$1.50/M	Flat
- [X] gemini-3.1-flash-image-preview	$0.25/M (text)	$0.067/image	Flat
- [X] gemini-3.1-pro-preview	$2/M → $4/M	$12/M → $18/M	≤200k / >200k
- [ ] gemini-3-pro-image-preview	$2.00/M (text)	$0.134/image	Flat
- [ ] gemini-3-pro-preview (deprecated)	


"""




if __name__ == "__main__":
    clear_terminal()

    # Refresh local_models.json from DB, then audit + save all_model_keys.json / dataclass_gaps.json:
    asyncio.run(save_all_models())

    # Audit coverage against existing local_models.json (no DB hit):
    # audit_dataclass_coverage()

    overrides = {
        "name": "gemini-3-pro-image-preview",
        "common_name": "Gemini 3 Pro Image Preview",
        "model_class": "gemini-3-pro-image-preview",
        # "controls": {
        #     "reasoning_effort": {"enum": ["low", "medium", "high"], "type": "string", "default": "high"},
        # },
    }

    # new_model = asyncio.run(duplicate_ai_model("gemini-3.1-flash-image-preview", overrides))
    # vcprint(new_model, "[Duplicator] New model", color="blue")