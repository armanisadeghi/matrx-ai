from __future__ import annotations

import asyncio

from matrx_utils import clear_terminal, vcprint

from db.custom import cxm


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

if __name__ == "__main__":
    clear_terminal()
    # response = asyncio.run(test_load_conversation())
    # vcprint(response, "[CX MANAGER TEST] Load Conversation", color="green")
    
    # response = asyncio.run(test_get_conversation_data())
    # vcprint(response, "[CX MANAGER TEST] Get Conversation Data", color="green")
    
    response = asyncio.run(test_get_conversation_unified_config())
    vcprint(response, "[CX MANAGER TEST] Get Conversation Unified Config", color="green")
    
    # response = asyncio.run(test_get_full_conversation())
    # vcprint(response, "[CX MANAGER TEST] Get Full Conversation", color="green")