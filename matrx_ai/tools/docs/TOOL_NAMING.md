## Tool Naming Best Practices

**Name structure:**
- Start with a verb — `get_`, `list_`, `search_`, `create_`, `update_`, `delete_`
- Include a service prefix to avoid collisions — `slack_send_message` not `send_message`, `github_create_issue` not `create_issue`
- Use `snake_case` consistently (or `camelCase`, but pick one and stick to it)
- Be specific and descriptive — `calculator_arithmetic` not just `calculate`
- Keep names unique across all tools the agent has access to
- Namespace by service *and* resource when you have many tools — e.g. `asana_projects_search`, `asana_users_search`

**Descriptions:**
- Descriptions must narrowly and unambiguously describe the tool's functionality
- Write them like you're onboarding a new hire — make implicit context explicit (specialized query formats, niche terminology, resource relationships)
- Description must precisely match actual behavior — no aspirational descriptions
- Include tool annotations: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`

## Argument / Parameter Best Practices

- Name parameters unambiguously — use `user_id` not `user`, `channel_name` not `name`
- Enforce strict input schemas with JSON Schema (types, required fields, enums)
- Prefer human-readable identifiers over UUIDs where possible — agents hallucinate less with semantic names
- Add a `description` to every parameter in the schema
- Use enums to constrain values when the set is finite (e.g. `response_format: "concise" | "detailed"`)
- Provide sensible defaults for pagination, limits, and filters
- Make error responses actionable — include examples of valid input, not just error codes

## Tool Design (Bonus)

- Fewer, smarter tools > many thin wrappers — consolidate multi-step workflows into a single tool (e.g. `schedule_event` instead of `list_users` + `list_events` + `create_event`)
- Each tool should have a clear, distinct purpose with no overlap
- Return only high-signal data — skip `uuid`, `mime_type`, `256px_image_url` in favor of `name`, `image_url`, `file_type`
- Implement pagination/truncation with helpful steering messages when results are trimmed
- Prefix vs. suffix namespacing has measurable performance differences across LLMs — evaluate for your use case

## Output Schema:

- Be specific 
- Do not lose valuable information
- To get the proper output schema, either carefully review the code or run the function once and use a real output
- Do not bloat the data with things the AI Agent cannot use, but don't leave out information that would be valuable for the user or the AI Sgent.


- Example Schema:
```json
{
  "type": "object",
  "properties": {
    "date": {
      "type": "string",
      "description": "Current date formatted as day of week, month day, year (e.g. Monday, February 15, 2026)"
    },
    "status": {
      "type": "string",
      "description": "Status of the API response (e.g., 'ok')"
    },
    "articles": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "Direct URL to the full article"
          },
          "title": {
            "type": "string",
            "description": "Article headline"
          },
          "author": {
            "type": [
              "string",
              "null"
            ],
            "description": "Article author name"
          },
          "source": {
            "type": "object",
            "properties": {
              "id": {
                "type": [
                  "string",
                  "null"
                ],
                "description": "ID of the source"
              },
              "name": {
                "type": "string",
                "description": "Name of the publishing source"
              }
            },
            "description": "Details of the publishing source"
          },
          "content": {
            "type": [
              "string",
              "null"
            ],
            "description": "Snippet or full content of the article"
          },
          "urlToImage": {
            "type": [
              "string",
              "null"
            ],
            "description": "URL to the article's featured image"
          },
          "description": {
            "type": [
              "string",
              "null"
            ],
            "description": "Brief summary of the article"
          },
          "publishedAt": {
            "type": [
              "string",
              "null"
            ],
            "description": "ISO 8601 publication timestamp"
          }
        }
      },
      "description": "List of headline articles"
    },
    "totalResults": {
      "type": "integer",
      "description": "Total number of results available from the API"
    }
  }
}```


## Example Tool Entry:
[
  {
    "id": "f570b5d4-86bc-4345-9241-dc236bc5c25b",
    "name": "get_news_headlines",
    "description": "Fetch current top news headlines. Filter by country, category, sources, or keyword query. Returns article titles, sources, descriptions, and URLs. At least one of country, sources, or category is required.",
    "parameters": {
      "query": {
        "type": "string",
        "description": "Keyword or phrase to search within headlines."
      },
      "country": {
        "enum": [
          "us",
          "gb",
          "fr",
          "de",
          "ca",
          "au",
          "in",
          "jp",
          "br",
          "mx",
          "it",
          "es",
          "nl",
          "se",
          "no",
          "za",
          "ar",
          "eg",
          "kr",
          "tw",
          "hk",
          "sg",
          "nz",
          "ie",
          "at",
          "ch",
          "be",
          "pt",
          "pl",
          "ru"
        ],
        "type": "string",
        "description": "Two-letter ISO 3166-1 country code."
      },
      "sources": {
        "type": "string",
        "description": "Comma-separated news source IDs (e.g. bbc-news,cnn). Cannot be combined with country."
      },
      "category": {
        "enum": [
          "business",
          "entertainment",
          "general",
          "health",
          "science",
          "sports",
          "technology"
        ],
        "type": "string",
        "description": "News category to filter by."
      },
      "language": {
        "enum": [
          "en",
          "es",
          "fr",
          "de",
          "it",
          "pt",
          "nl",
          "sv",
          "no",
          "ar",
          "he",
          "zh",
          "ru"
        ],
        "type": "string",
        "default": "en",
        "description": "Two-letter language code for results."
      }
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "date": {
          "type": "string",
          "description": "Current date formatted as day of week, month day, year (e.g. Monday, February 15, 2026)"
        },
        "status": {
          "type": "string",
          "description": "Status of the API response (e.g., 'ok')"
        },
        "articles": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "url": {
                "type": "string",
                "description": "Direct URL to the full article"
              },
              "title": {
                "type": "string",
                "description": "Article headline"
              },
              "author": {
                "type": [
                  "string",
                  "null"
                ],
                "description": "Article author name"
              },
              "source": {
                "type": "object",
                "properties": {
                  "id": {
                    "type": [
                      "string",
                      "null"
                    ],
                    "description": "ID of the source"
                  },
                  "name": {
                    "type": "string",
                    "description": "Name of the publishing source"
                  }
                },
                "description": "Details of the publishing source"
              },
              "content": {
                "type": [
                  "string",
                  "null"
                ],
                "description": "Snippet or full content of the article"
              },
              "urlToImage": {
                "type": [
                  "string",
                  "null"
                ],
                "description": "URL to the article's featured image"
              },
              "description": {
                "type": [
                  "string",
                  "null"
                ],
                "description": "Brief summary of the article"
              },
              "publishedAt": {
                "type": [
                  "string",
                  "null"
                ],
                "description": "ISO 8601 publication timestamp"
              }
            }
          },
          "description": "List of headline articles"
        },
        "totalResults": {
          "type": "integer",
          "description": "Total number of results available from the API"
        }
      }
    },
    "annotations": [
      {
        "type": "readOnlyHint",
        "value": true
      },
      {
        "type": "openWorldHint",
        "value": true
      }
    ],
    "function_path": "ai.tool_system.implementations.news.get_news_headlines",
    "category": "data",
    "tags": [
      "news",
      "headlines",
      "api"
    ],
    "icon": null,
    "is_active": true,
    "version": "1.0.0",
    "created_at": "2026-02-16 02:34:16.976423+00",
    "updated_at": "2026-02-16 02:34:16.976423+00"
  }
]