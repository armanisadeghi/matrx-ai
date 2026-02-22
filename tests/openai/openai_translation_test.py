from typing import Any, Dict, List, Union
from openai.types.responses import (
    Response as OpenAIResponse,
    ResponseOutputItem as OpenAIResponseOutputItem,
    ResponseOutputMessage as OpenAIResponseOutputMessage,
)
from matrx_utils import vcprint, clear_terminal
from config.unified_config import (
    UnifiedConfig,
    TextContent,
    ToolCallContent,
    UnifiedMessage,
    ThinkingContent,
    WebSearchCallContent,
    ToolResultContent
)
from config.unified_config import OpenAITranslator

clear_terminal()

# Dictionary representing the raw response data
response_data = {
    "id": "resp_0a16d8c172123aeb006955587f41f481a0b884a4f06bedc90c",
    "created_at": 1767200895.0,
    "error": None,
    "incomplete_details": None,
    "instructions": None,
    "metadata": {},
    "model": "gpt-5.1-2025-11-13",
    "object": "response",
    "output": [
        {
            "id": "rs_0a16d8c172123aeb006955587ff73081a099639e7f57bdd432",
            "summary": [
                {
                    "text": "**Searching for positive news**\n\nI need to find a positive news story from today, December 31, 2025. The user is looking for something uplifting, possibly related to science, the environment, or medicine. I'll use the web tool to execute a search query focusing on today's date for recent and relevant news. I\u2019ll make sure to pull just one great story that fits what the user is interested in! Let's see what we can find.",
                    "type": "summary_text",
                }
            ],
            "type": "reasoning",
            "content": None,
            "encrypted_content": None,
            "status": None,
        },
        {
            "id": "rs_027483162c55a1a7006955b7816d08819e8b3198bd1a10794d",
            "summary": [
                {
                    "text": '**Researching plasma generation updates**\n\nI\'m noticing that the Space Forge site doesn\u2019t have a December 31 update regarding plasma generation, so perhaps they shared something on social media. Although, I\u2019ve found reputable sources that reported on this. Scientific American, Semiconductor Today, and SatNews have covered it. \n\nI need to pick some citations, including Scientific American and others, ensuring I cite major claims properly. I\u2019ll summarize by saying: "Today, December 31, 2025, Space Forge generated plasma aboard ForgeStar-1, reaching 1,000\u00b0C."',
                    "type": "summary_text",
                },
                {
                    "text": '**Crafting significance statement**\n\nI\u2019m defining the significance of this event: "This proves that extreme thermal conditions needed for gas-phase crystal growth can be created and controlled in low Earth orbit, paving the way for ultra-pure semiconductors, which the company claims can be up to 4,000 times purer. This could benefit 5G, electric vehicles, and more." \n\nI\u2019ll reference Scientific American and Semiconductor Today for the event, and cite Satellite News or Tom\'s Hardware for the 4,000x claim. I\u2019ll also include a note asking if the user wants more positive stories today, offering to send a link or summary.',
                    "type": "summary_text",
                },
                {
                    "text": "**Ensuring citation accuracy**\n\nI need to make sure I include the right citations for the event and the claim about 4,000x purity, as well as noting that this is the first time plasma has been generated aboard a commercial satellite. Semiconductor Today emphasizes that it's a world-first. It's essential to ensure these citations accurately reflect the claims made. I should open the Scientific American article content to confirm that it explicitly states these facts. So, I'll get that started now!",
                    "type": "summary_text",
                },
            ],
            "type": "reasoning",
            "content": None,
            "encrypted_content": "gAAAAABpVbe8kW7qofjDhrFOIj1Rod21KCKP5SkpRojMkkgkeO4tijewJJ10c1OTs4pZY78Q1v5UZTFc8mQ-6PB7r3rUMMh-FCNAvc3Dsx2WsDA3F6jr6eangQduNa9G7L_53AB1iB7SKHngCTtk4WHcUT3mxSwUUqoMDOIg-L2CSTzR7yZbSclIw0DWLRcP3iVxq_fwZPbuLPbP49V_kXR4dxMvH7neTHL_xxQHm8v6N91WhNpjbBxJRHABlHz-d9DQg0EYFmMPUp5p5LvzC4-oo9XQ61PDu9dLKMDZZM1EjYShqzRw5kG--tCyGK7rZ6ps9SIzkopKCqCU9CNsFJAkqQO5pnWji3faVcwIE3-_z5hbQYtr9dLUTVzf3y80JwuNwzQUjkuUCySKFTekil69YBTItU7ZjHBGHySpPj2jFUxfx3tWh5g7-rmObo0eDBUZdGfDcpI4ndrF151Mv6t4a-JB8ZFBynfDzbLdCK0uItEaXGOPjpsH1HYXQjZMcJ2Ekmf5VCrYTqlmbjDtLN7477-fUVWJGeHXH1d5cBrdwEQMidb83hvXZ9GBZijGvg6AjnedilR1YA8pxmhWRd93VLV5h_lCwYSr5fqo57FcYqQlR2q7oRWeGyn88CluytrbQ8uQUhUNhsoIUIPwi0eEsEUem9nWEazI2R88fCyNqnEBPJDhgZ1jDMRG0P3THe5Tj0hUSBrtRjKMIzx_vTfAwnj6E-mV9Y-eqb1Km-gC1a0-ml0N3HeGC-T7-CjJ7hZ8KgKrtoTdCrhqDLFvXYHDy6-sJsNlM9XMT5g-Z_6E5dIcqkznJyaL2Y4iDb2pJbe3J4eqOENoj4jN2zx5Oe0yy9lnB0Lhbu1qUe7qY1sByzRTPDTHswVA6j_37b9et7_bEhRHj1wB3-GKWN9_Txt48OEmxJ0NV6juSRX3KU4F8qCtYpzy0lPJ2TFFpharO4pmrmBKd2A22yzKu_xFyzUlvtzJohtvypO1Jw6sZckMNA3DwSmjb5YMDFjhnVBLm8-AxPEI2LTorz_H3dyPLA2JrCTmjVmQzAJTxlWt3eaeL4E5rn6OZiE6dFDmgYFmd5xQlWsIjh8p2mjCQKRNJvCbGcsIaPlL4l7zxXn8Gv37DI3ZevPtbaQrt0UxWQThZ5o3EXmw8yHaJnzLUMVC6Mja_ikUYBIBVYB_mG3ta1eg6zugKsilwHLiWu8bQJlNRg2Bcs-hoywljQFhUVCzb-tnd50QGf8g45VyvBgXv9MIZooq_cqdQ-zRVfbsVpDZPOyHJ5LbNEHgsxHBThsv3f1UddaPT18MMIhJzQEDm8_-PMhFpriJnre7P1KaBxl4FuyhvleC9uG5Yruynh-cgoSRbvjpil8ScQNVKYaNMm8g8GuW1niNTiWhqVK3gVIBASar2S1bdVXjGpKDsbAeic4ByRVvLS_J1mP9HG2tdWm3E6yWiOBPWdA1M_9-Ffad2gPh332ozpNmQ56SIvne2yaqHy_TozBboZi_zm4SWRoo7F9kS7NFNPLMeY_XAa2DPx912zDZqPr-VqOV1WWhoE3NciiSJYB_euBMeHEDtv-2fOGQiv-GnAmJqsHh8SowSgK7omTmzNh2RdgbDKLanQDKiAEx41WXm6C0GMS1MSNQ4Pv2XGqiEpmLLzdYdqrhg5aDf3jfV8K0bRwjd9h1oFZGCr9JgwOzwuCtBi8cdthi579rCyIl81kwmTeZePGT4JvnthNEubfQhrfStj1edwQY821B4lb-XpRoLIyVhGmmqUqrkPwdmAlJK1gxQmPlNWBHcyzwRez0NJL9e2aXmrIvKTw3jNKXIWNV26eVgiS0gw-Ng5CTvrvO8YWQmA4cm8E23pRFfA9i6u9EoHG7sEgwg7msItZlmqUlp1fOaojHsvtGTrBPg01CAeYlKQt9u1IyPi6T8lPqnxULj4tBfVm77fW07tCWnCfPgUf0oatjy00ENfXf8WN1sDE_DczAYJBerk92WTY0R0qK__BWtGdsnAHCYWIYzqV2G9mVejyIkTnmKd4YNhk1LAAFHeUndEagb3lq3uYwgW8nKAYlD0xYWz7b2kCeTHH1SA0A1gcsPYMxveX87rnDgKDZHMOVIZgtZyBN9Ocxk58Q4BV5koOZTNwQKJabua1p_oe8wnSpOQRJJGtO4myjiJZgC8OxsHcb4iOPIIxc4rkM02WfxOBBUS5Qmjg8q5LR4oH41MMKBk_ysFXGD5tnXSPLen6dgbMcUjqAeCK6N8DDlcW0TnIXBfjjHvXBk0zWPLg7t6Ze1z0MVAqOAa5VDRdQ6v4ofuEHqD1OCZvFV-ANb6jY5hNunTu7IegPSIkxehz1W1NIEYijVihcoR9sAKAJK8vGcTAt7dYLRTO7SL-iU9NLRuPNzup--UMlKbYxEFgBjT77T3whq2-yojUvCfcblQteojZkk5syCEpTMNwcLmlFstNQUEH9mbroZwyO8F_RAWu-Y4RpG7FOYHTueZ0MjmFuqyackWf2WhbQ05J33KnHhZy2qO4eie-LuZN6uaAv7JeQmBD13klXwRTvWj10pfidGm51wRgcbDvR4o_Cq_SqcM-rGnkQLQcUplbUng8Q_-8dgG2jNnowdkQ1ZxImqc7H6xyi5M078vmE-SFH02IOspAQEMa-lIJFB_6Ae00nWiAwrsxlmU27iU6IPQmQvND0qNncIhnLdBaic9-hDqrcFVrTILPSL8YVujLe_gKFo-74ZN6Q1LRJ27JgSvwYNoeRDJ9XgPT-SHhEzv_EoIGrqyledIBPFhpeRiyCVfbSshB6Kv3hFVdcvPgu-w0mB7AIzwdpelAIYAoXu321Yq08tUp0q3e-CT3Ko_gM6xM6f8TodM3PHFSzxVY7itsanmbQbMP9xDsaw8nTd7tHq88IdAH-_JfYCbhxyHomlC9y1dZCeT--kdXsuZs-Uz3ooHGfEUzKF1ilLIWgEnMyjUpPrrUYlE7Up31OoGDHp9EMJVkscZUiMqDyy0IGcZfN2RoxzE8aDN8bfnEYTQkStwzJLIChvzjSnCcwbwogzZerBRbvW_TG0MOYIX5WfLjD1Ps94ouEagR68_YZ1XnzSuIYgDg1emfQTeb5K6kAnbHzu5wUQvAAWvHRdlxnDuN1KN-1FsmWW5v1DTFIg8i0iebpl7d1VAN01pz63tgJrVxCd00QB4YDTWpvLyNYMbF1xZc3dJGfbEYvD90QLg3S6r4bGX_gepDhQvcF0aux71WIF5dXcJ1szPw7AWfeXzMt-ku7t62s-nYoTg3i5zOMP2beN3Vdr1XNn_kAGi0IXETvvj7hFJXh0LlTVpyJZVB98UIAbSIZ0s5SAkafCp8_AkSwPZLncv8Q25kaVfKzq64ZbX9knAJzHYuhW4PAR2tlicmEwXrsNmNpgLdC-kFL_bMuOaXALmInwehIfcDlOmQji_XKaNxTL31lsEYACccQdvGnfCLxpu7U4Bwt9W8flQLr82ZxG9GF7XwXn_vmhfl4oRnISfmjbFQrr16LrmNF-fn_0GrVXAYJfQNi-tHlEWKG1g5KvZYkJbKCU2bgYOlb3V39GPV0aE7ffLFPY-OXJU9JhDsb43MGnw2WSGuGcV2nJA8A9Ca_MHZTyTbuuvRpoQ-5Z-jGpXZ2kXKaYHImGoR8nLQ31AMTljTh34vuJ5MvC-UPt8Lsnvosq42opjtMwK5Uoi_zTjZC7yJdN0bheLQxp_Lh3skvndENr6lnlGYUHwDtym3BfTBhAfNxVn1YY9zZa7fjJZSkag2GTZjF0B7YPXkuKnFL6QSNcku84wykrNB1hETsOF_15mtMHU4EhR-SgeD2DzOGz38qT1AcssLpxZa3fmlRw0zxSBc-YLefaacpEGO_7OdapYsMnY9rXota381AA_4dZLB1bKOWR9CEgb2kgjDpfcIhRIsP_7MPfvCPt0iPoDr41XqGr7H1F4DxElJ7oqNWHIys0qN3vSqh5l7vpOmcGQtN",
            "status": None,
        },
        {
            "id": "ws_0a16d8c172123aeb006955588402c481a096d2645bee7a9be5",
            "action": {
                "query": "good news positive news December 31 2025 breakthrough discovery",
                "type": "search",
                "sources": None,
            },
            "status": "completed",
            "type": "web_search_call",
        },
        {
            "id": "rs_0a16d8c172123aeb00695558935a0881a0bf1a647cc846ee99",
            "summary": [
                {
                    "text": '**Searching for positive news**\n\nI need to find a positive story specifically from today, December 31, 2025. I\'ve noticed some general "year in review" articles and positive science updates, but the user asked for something published today. I should refine my search for "December 31, 2025 good news." I\u2019ll aim for a mainstream piece, possibly something like an article about a malaria vaccine cost drop or conservation success. I\u2019ll focus on getting a concrete story.',
                    "type": "summary_text",
                }
            ],
            "type": "reasoning",
            "content": None,
            "encrypted_content": None,
            "status": None,
        },
        {
            "id": "ws_0a16d8c172123aeb00695558953d2081a0b5781268222e73c8",
            "action": {
                "query": '"December 31, 2025" "good news" "breakthrough"',
                "type": "search",
                "sources": None,
            },
            "status": "completed",
            "type": "web_search_call",
        },
        {
            "id": "rs_0a16d8c172123aeb00695558a09c5881a0a02af404b0d209f2",
            "summary": [
                {
                    "text": '**Summarizing conservation success**\n\nThere\u2019s a recent article titled "DEC completes spruce grouse restoration effort" published on December 31, 2025, detailing the successful conservation of the endangered spruce grouse in New York. This counts as positive news since it highlights a successful effort in wildlife restoration in the user\'s state. I should summarize the key points briefly, providing just enough context to explain why it\u2019s a good development, and cite the source as FingerLakes1.com.',
                    "type": "summary_text",
                },
                {
                    "text": "**Finalizing spruce grouse summary**\n\nI\u2019m reviewing the details of the article to ensure I have everything right. The New York State Department of Environmental Conservation has completed its 13-year spruce grouse recovery program in the Adirondacks, releasing a total of 363 adults and 711 chicks. Their final release included 50 adults in summer 2025, and now they're focusing on monitoring and habitat management. This is a major milestone for conservation, showing a shift from decline to hope for this endangered species.",
                    "type": "summary_text",
                },
                {
                    "text": "**Defining spruce grouse**\n\nI'll quickly define the spruce grouse as a rare bird found in cold forests, situated near the southern edge of its range in New York. This is positive news as it represents a long-term investment in wildlife conservation and showcases cross-border cooperation efforts for species protection. Overall, this achievement is significant for restoring populations. I'll make sure to include the explicit date of December 31, 2025, in my response.",
                    "type": "summary_text",
                },
            ],
            "type": "reasoning",
            "content": None,
            "encrypted_content": None,
            "status": None,
        },
        {
            "id": "msg_0a16d8c172123aeb00695558a8999481a0ba1cf75662ed604e",
            "content": [
                {
                    "annotations": [
                        {
                            "end_index": 796,
                            "start_index": 669,
                            "title": "DEC completes spruce grouse restoration effort",
                            "type": "url_citation",
                            "url": "https://www.fingerlakes1.com/2025/12/31/dec-completes-spruce-grouse-restoration-effort/?utm_source=openai",
                        }
                    ],
                    "text": "One uplifting story from today (December 31, 2025):\n\nNew York\u2019s Department of Environmental Conservation announced it has completed the release phase of a 13\u2011year program to rescue the endangered spruce grouse, one of the state\u2019s rarest birds, in the Adirondacks. \n\nSince 2013, biologists and partners in Canada and Maine have moved hundreds of adult birds and chicks into carefully selected forest habitats to rebuild the population. With the final group of birds released this past summer, officials say the focus can now shift from emergency releases to long\u2011term monitoring and habitat protection\u2014meaning the species is no longer in immediate freefall in New York. ([fingerlakes1.com](https://www.fingerlakes1.com/2025/12/31/dec-completes-spruce-grouse-restoration-effort/?utm_source=openai))\n\nSo, today\u2019s good news: a long, patient conservation effort has reached a major milestone, giving a threatened species a real chance to recover.",
                    "type": "output_text",
                    "logprobs": [],
                }
            ],
            "role": "assistant",
            "status": "completed",
            "type": "message",
        },
        {
            "id": "rs_086e678647afe2e60069559b4c6e1c81a2910ecb2b56433cea",
            "summary": [
                {
                    "text": "**Fetching US headlines**\n\nI think it\u2019s time to use the tool to get the latest headlines from the US. I\u2019ll call the functions.api_news_fetch_headlines with the country set to 'us.' Since we don\u2019t need to run multiple calls in parallel for this, it should be straightforward. After that, I\u2019ll present the headlines clearly for the user. I\u2019m eager to get this information out efficiently!",
                    "type": "summary_text",
                }
            ],
            "type": "reasoning",
            "content": None,
            "encrypted_content": None,
            "status": None,
        },
        {
            "arguments": '{"country": "us"}',
            "call_id": "call_FIgJkqN3zm7dxecf0pTjZJdD",
            "name": "api_news_fetch_headlines",
            "type": "function_call",
            "id": "fc_086e678647afe2e60069559b4e798481a2b11861b95ccbe491",
            "status": "completed",
            "parsed_arguments": None,
        },
    ],
    "parallel_tool_calls": True,
    "temperature": 1.0,
    "tool_choice": "auto",
    "tools": [
        {
            "type": "web_search_preview",
            "search_context_size": "medium",
            "user_location": {
                "type": "approximate",
                "city": None,
                "country": "US",
                "region": None,
                "timezone": None,
            },
        }
    ],
    "top_p": 1.0,
    "background": False,
    "conversation": None,
    "max_output_tokens": None,
    "max_tool_calls": None,
    "previous_response_id": None,
    "prompt": None,
    "prompt_cache_key": None,
    "reasoning": {"effort": "high", "generate_summary": None, "summary": "detailed"},
    "safety_identifier": None,
    "service_tier": "default",
    "status": "completed",
    "text": {"format": {"type": "text"}, "verbosity": "medium"},
    "top_logprobs": 0,
    "truncation": "disabled",
    "usage": {
        "input_tokens": 12296,
        "input_tokens_details": {"cached_tokens": 0},
        "output_tokens": 1076,
        "output_tokens_details": {"reasoning_tokens": 893},
        "total_tokens": 13372,
    },
    "user": None,
    "billing": {"payer": "developer"},
    "completed_at": 1767200936,
    "prompt_cache_retention": None,
    "store": True,
}

# Parse the dictionary into a proper OpenAIResponse object
response: OpenAIResponse = OpenAIResponse.model_validate(response_data)

translator = OpenAITranslator()
unified_response = translator.from_openai(response)
vcprint(unified_response, "Unified Response", color="green", verbose=True)


# config = UnifiedConfig.from_dict(unified_response.to_dict())
# back_to_openai = translator.to_openai(config, "openai_reasoning")
# vcprint(back_to_openai, "Back to OpenAI", color="magenta", verbose=True)