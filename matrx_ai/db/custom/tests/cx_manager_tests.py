from __future__ import annotations

import asyncio

from matrx_utils import clear_terminal, vcprint

from matrx_ai.db.custom import cxm
from matrx_ai.providers.openai.translator import OpenAITranslator


async def test_load_conversation():
    conversation_id = "b673289f-c0d0-4201-9221-8d786fe79ca7"
    conversation = await cxm.conversation.load_cx_conversation(id=conversation_id)

    return conversation


async def test_get_conversation_data():
    conversation_id = "b673289f-c0d0-4201-9221-8d786fe79ca7"
    conversation_data = await cxm.get_conversation_data(conversation_id)
    return conversation_data

async def test_get_conversation_unified_config():
    conversation_id = "b673289f-c0d0-4201-9221-8d786fe79ca7"
    unified_config = await cxm.get_conversation_unified_config(conversation_id)
    return unified_config

async def test_get_full_conversation():
    conversation_id = "b673289f-c0d0-4201-9221-8d786fe79ca7"
    full_conversation = await cxm.get_full_conversation(conversation_id)
    return full_conversation

async def test_get_convo_to_openai_format():
    conversation_id = "f85bae35-f659-4450-85ce-ce8ef09a1b48"
    unified_config = await cxm.get_conversation_unified_config(conversation_id)
    vcprint(unified_config, "[CX MANAGER TEST] Unified Config", color="cyan")

    translator = OpenAITranslator()

    convo_to_openai = translator.to_openai(unified_config, "openai_standard")
    
    vcprint(convo_to_openai, "[CX MANAGER TEST] Convo to OpenAI Format", color="cyan")
    
    return convo_to_openai


if __name__ == "__main__":
    clear_terminal()
    # response = asyncio.run(test_load_conversation())
    # vcprint(response, "[CX MANAGER TEST] Load Conversation", color="green")
    
    # response = asyncio.run(test_get_conversation_data())
    # vcprint(response, "[CX MANAGER TEST] Get Conversation Data", color="green")
    
    # response = asyncio.run(test_get_conversation_unified_config())
    # vcprint(response, "[CX MANAGER TEST] Get Conversation Unified Config", color="green")
    
    # response = asyncio.run(test_get_full_conversation())
    # vcprint(response, "[CX MANAGER TEST] Get Full Conversation", color="green")
    
    response = asyncio.run(test_get_convo_to_openai_format())
    vcprint(response, "[CX MANAGER TEST] Get Convo to OpenAI Format", color="green")