# Tool Naming Overhaul

## Convention: `{prefix}_{action}` — always

Every tool name must follow `{domain_prefix}_{verb_noun}` — the prefix makes the category immediately scannable, the action tells the model what it does.

**Current issues:**
- `calculate` — no prefix
- `text_analyze`, `regex_extract` — `text_` is fine but `regex_extract` breaks the verb-first rule
- `web_search`, `web_read`, `web_research` — `web_` is fine but `web_research` conflicts with the `research_` domain that's expanding
- `execute_python`, `store_html`, `fetch_code` — no prefix, mixed verb order
- SEO tools — `check_meta_*` / `get_keyword_search_data` — no `seo_` prefix
- Travel tools — `get_location`, `get_weather`, etc. — no `travel_` prefix
- User lists — `create_user_list` / `create_simple_list` / `get_user_lists` etc. — changing `user_list` → `personal_list`
- User table — `create_user_generated_table` — changing `user` → `personal_table`
- Interaction — `ask_user_questions` — no prefix
- News — `get_news_headlines` — `news_` prefix missing

---

## Full Rename Table

Edit the **Proposed Name** column. Mark **Keep?** as `✅` or change to your preferred name.

### 🧮 Math

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `calculate` | `math_calculate` | math | ✅ | Adds `math_` prefix |

---

### 📝 Text

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `text_analyze` | `text_analyze` | text | ✅ | Already correct |
| `regex_extract` | `text_regex_extract` | text | ✅ | Adds `text_` prefix, keeps verb-noun |

---

### 🌐 Web

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `web_search` | `web_search` | web | ✅ | Already correct |
| `web_read` | `web_read` | web | ✅ | Already correct |
| `web_research` | `research_web` | research | ✅ **DONE** | Moves to `research_` domain — see Research section |

---

### 🗄️ Database

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `db_query` | `db_query` | database | ✅ | Already correct |
| `db_insert` | `db_insert` | database | ✅ | Already correct |
| `db_update` | `db_update` | database | ✅ | Already correct |
| `db_schema` | `db_schema` | database | ✅ | Already correct |

---

### 💾 Memory

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `memory_store` | `memory_store` | memory | ✅ | Already correct |
| `memory_recall` | `memory_recall` | memory | ✅ | Already correct |
| `memory_search` | `memory_search` | memory | ✅ | Already correct |
| `memory_update` | `memory_update` | memory | ✅ | Already correct |
| `memory_forget` | `memory_forget` | memory | ✅ | Already correct |

---

### 📁 Filesystem

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `fs_read` | `fs_read` | filesystem | ✅ | Already correct |
| `fs_write` | `fs_write` | filesystem | ✅ | Already correct |
| `fs_list` | `fs_list` | filesystem | ✅ | Already correct |
| `fs_search` | `fs_search` | filesystem | ✅ | Already correct |
| `fs_mkdir` | `fs_mkdir` | filesystem | ✅ | Already correct |

---

### 🖥️ Shell

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `shell_execute` | `shell_execute` | shell | ✅ | Already correct |
| `shell_python` | `shell_python` | shell | ✅ | Already correct |

---

### 🌍 Browser

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `browser_navigate` | `browser_navigate` | browser | ✅ | Already correct |
| `browser_click` | `browser_click` | browser | ✅ | Already correct |
| `browser_type_text` | `browser_type_text` | browser | ✅ | Already correct |
| `browser_screenshot` | `browser_screenshot` | browser | ✅ | Already correct |

---

### 💻 Code

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `execute_python` | `code_execute_python` | code | ✅ | Adds `code_` prefix |
| `store_html` | `code_store_html` | code | ✅ | Adds `code_` prefix |
| `fetch_code` | `code_fetch_code` + `code_fetch_tree` | code | ✅ **DONE** | Split into two focused tools |

---

### 📰 News

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `get_news_headlines` | `news_get_headlines` | news | ✅ | Adds `news_` prefix, prefix-first ordering |

---

### 🔍 SEO

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `check_meta_titles` | `seo_check_meta_titles` | seo | ✅ | Adds `seo_` prefix |
| `check_meta_descriptions` | `seo_check_meta_descriptions` | seo | ✅ | Adds `seo_` prefix |
| `check_meta_tags_batch` | `seo_check_meta_tags_batch` | seo | ✅ | Adds `seo_` prefix |
| `get_keyword_search_data` | `seo_get_keyword_data` | seo | ✅ | Adds `seo_` prefix, shortened `_search` (redundant for kw data) |

---

### 🔬 Research

> **Expanding soon.** Moving `web_research` here and building out the research domain.

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `web_research` | `research_web` | research | ✅ | First tool of the research domain |
| *(future)* | `research_summarize` | research | — | Summarize content or search results |
| *(future)* | `research_compare` | research | — | Compare multiple sources/entities |
| *(future)* | `research_extract_facts` | research | — | Extract structured facts from text |
| *(future)* | `research_cite` | research | — | Generate citations |

---

### ✈️ Travel

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `get_location` | `travel_get_location` | travel | ✅ | Adds `travel_` prefix |
| `get_weather` | `travel_get_weather` | travel | ✅ | Adds `travel_` prefix |
| `get_restaurants` | `travel_get_restaurants` | travel | ✅ | Adds `travel_` prefix |
| `get_activities` | `travel_get_activities` | travel | ✅ | Adds `travel_` prefix |
| `get_events` | `travel_get_events` | travel | ✅ | Adds `travel_` prefix |
| `create_travel_summary` | `travel_create_summary` | travel | ✅ | Prefix-first ordering |

---

### 📋 Personal Lists

> `user_list` → `personal_list`

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `create_user_list` | `personal_list_create` | personal_lists | ✅ | `user` → `personal`, prefix-first |
| `create_simple_list` | `personal_list_create_simple` | personal_lists | ✅ | Disambiguates from full-featured create |
| `get_user_lists` | `userlist_get_all` | user_lists | ✅ **DONE** | Aligned with userlist_* module naming |
| `get_list_details` | `personal_list_get_details` | personal_lists | ✅ | Adds domain prefix |
| `update_list_item` | `personal_list_update_item` | personal_lists | ✅ | Adds domain prefix |
| `batch_update_list_items` | `personal_list_batch_update` | personal_lists | ✅ | Shorter, prefix-first |

---

### 📊 Personal Tables

> `user_table` → `personal_table`

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `create_user_generated_table` | `personal_table_create` | personal_tables | ✅ | Drops verbose `_generated`, prefix-first |
| *(future)* | `personal_table_get` | personal_tables | — | Retrieve existing tables |
| *(future)* | `personal_table_update` | personal_tables | — | Modify table data |
| *(future)* | `personal_table_delete` | personal_tables | — | Delete a table |

---

### 💬 Interaction

| Current Name | Proposed Name | Category | Keep? | Notes |
|---|---|---|---|---|
| `ask_user_questions` | `interaction_ask` | interaction | ✅ **DONE** | Prefix-first; drops redundant `_user_questions` |

---

## Summary: What Needs to Change

### ✅ No changes needed (already correct pattern)
`text_analyze`, `web_search`, `web_read`, `db_query`, `db_insert`, `db_update`, `db_schema`, `memory_*` (all 5), `fs_*` (all 5), `shell_execute`, `shell_python`, `browser_*` (all 4)

### 🔄 Rename only (no logic change)

| Old | New |
|---|---|
| `calculate` | `math_calculate` |
| `regex_extract` | `text_regex_extract` |
| `execute_python` | `code_execute_python` |
| `store_html` | `code_store_html` |
| `fetch_code` | `code_fetch` |
| `get_news_headlines` | `news_get_headlines` |
| `check_meta_titles` | `seo_check_meta_titles` |
| `check_meta_descriptions` | `seo_check_meta_descriptions` |
| `check_meta_tags_batch` | `seo_check_meta_tags_batch` |
| `get_keyword_search_data` | `seo_get_keyword_data` |
| `web_research` | `research_web` |
| `get_location` | `travel_get_location` |
| `get_weather` | `travel_get_weather` |
| `get_restaurants` | `travel_get_restaurants` |
| `get_activities` | `travel_get_activities` |
| `get_events` | `travel_get_events` |
| `create_travel_summary` | `travel_create_summary` |
| `create_user_list` | `personal_list_create` |
| `create_simple_list` | `personal_list_create_simple` |
| `get_user_lists` | `userlist_get_all` |
| `get_list_details` | `personal_list_get_details` |
| `update_list_item` | `personal_list_update_item` |
| `batch_update_list_items` | `personal_list_batch_update` |
| `create_user_generated_table` | `personal_table_create` |
| `ask_user_questions` | `interact_ask` |

**Total: 25 tools renamed, 23 already correct.**
