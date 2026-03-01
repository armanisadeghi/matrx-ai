from .browser import (
    browser_click,
    browser_close,
    browser_get_element,
    browser_navigate,
    browser_screenshot,
    browser_scroll,
    browser_select_option,
    browser_type_text,
    browser_wait_for,
)
from .code import (
    code_execute_python,
    code_fetch_code,
    code_fetch_tree,
    code_store_html,
)
from .database import db_insert, db_query, db_schema, db_update
from .filesystem import fs_list, fs_mkdir, fs_read, fs_search, fs_write
from .math import math_calculate
from .memory import memory_forget, memory_recall, memory_search, memory_store, memory_update
from .news import news_get_headlines
from .personal_tables import (
    usertable_add_rows,
    usertable_create_advanced,
    usertable_delete_row,
    usertable_get_all,
    usertable_get_data,
    usertable_get_fields,
    usertable_get_metadata,
    usertable_search_data,
    usertable_update_row,
)
from .questionnaire import interaction_ask
from .seo import (
    seo_check_meta_descriptions,
    seo_check_meta_tags_batch,
    seo_check_meta_titles,
    seo_get_keyword_data,
)
from .shell import shell_execute, shell_python
from .text import text_analyze, text_regex_extract
from .travel import (
    travel_create_summary,
    travel_get_activities,
    travel_get_events,
    travel_get_location,
    travel_get_restaurants,
    travel_get_weather,
)
from .user_lists import (
    userlist_batch_update,
    userlist_create,
    userlist_create_simple,
    userlist_get_all,
    userlist_get_details,
    userlist_update_item,
)
from .user_tables import usertable_create
from .web import research_web, web_read, web_search

__all__ = [
    # Math
    "math_calculate",
    # Text
    "text_analyze", "text_regex_extract",
    # Web
    "web_search", "web_read",
    # Research
    "research_web",
    # Database
    "db_query", "db_insert", "db_update", "db_schema",
    # Memory
    "memory_store", "memory_recall", "memory_search", "memory_update", "memory_forget",
    # Filesystem
    "fs_read", "fs_write", "fs_list", "fs_search", "fs_mkdir",
    # Shell
    "shell_execute", "shell_python",
    # Browser
    "browser_navigate", "browser_click", "browser_type_text", "browser_screenshot", "browser_close",
    "browser_select_option", "browser_wait_for", "browser_get_element", "browser_scroll",
    # User Lists
    "userlist_create", "userlist_create_simple", "userlist_get_all",
    "userlist_get_details", "userlist_update_item", "userlist_batch_update",
    # SEO
    "seo_check_meta_titles", "seo_check_meta_descriptions", "seo_check_meta_tags_batch",
    "seo_get_keyword_data",
    # Code
    "code_store_html", "code_fetch_code", "code_fetch_tree", "code_execute_python",
    # News
    "news_get_headlines",
    # User Tables (simple)
    "usertable_create",
    # User Tables (advanced)
    "usertable_create_advanced",
    "usertable_get_all",
    "usertable_get_metadata",
    "usertable_get_fields",
    "usertable_get_data",
    "usertable_search_data",
    "usertable_add_rows",
    "usertable_update_row",
    "usertable_delete_row",
    # Interaction
    "interaction_ask",
    # Travel
    "travel_get_location", "travel_get_weather", "travel_get_restaurants",
    "travel_get_activities", "travel_get_events", "travel_create_summary",
]
