from .math import math_calculate
from .text import text_analyze, text_regex_extract
from .web import web_search, web_read, research_web
from .database import db_query, db_insert, db_update, db_schema
from .memory import memory_store, memory_recall, memory_search, memory_update, memory_forget
from .filesystem import fs_read, fs_write, fs_list, fs_search, fs_mkdir
from .shell import shell_execute, shell_python
from .browser import (
    browser_navigate, browser_click, browser_type_text, browser_screenshot, browser_close,
    browser_select_option, browser_wait_for, browser_get_element, browser_scroll,
)
from .user_lists import (
    userlist_create, userlist_create_simple, userlist_get_all,
    userlist_get_details, userlist_update_item, userlist_batch_update,
)
from .seo import (
    seo_check_meta_titles, seo_check_meta_descriptions, seo_check_meta_tags_batch,
    seo_get_keyword_data,
)
from .code import (
    code_store_html, code_fetch_code, code_fetch_tree, code_execute_python,
)
from .news import news_get_headlines
from .user_tables import usertable_create
from .personal_tables import (
    usertable_create_advanced,
    usertable_get_all,
    usertable_get_metadata,
    usertable_get_fields,
    usertable_get_data,
    usertable_search_data,
    usertable_add_rows,
    usertable_update_row,
    usertable_delete_row,
)
from .questionnaire import interaction_ask
from .travel import (
    travel_get_location, travel_get_weather, travel_get_restaurants,
    travel_get_activities, travel_get_events, travel_create_summary,
)

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
