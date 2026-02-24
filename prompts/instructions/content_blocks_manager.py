import uuid
from matrx_orm import BaseManager
from db.models import ContentBlocks
from db.managers.content_blocks import ContentBlocksDTO
from typing import Optional, Type, Any

def is_valid_uuid(value):
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


class ContentBlocksBase(BaseManager):
    def __init__(
        self,
        dto_class: Optional[Type[Any]] = None,
        fetch_on_init_limit: int = 200,
        fetch_on_init_with_warnings_off: str = "YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_100",
    ):
        self.dto_class = dto_class or ContentBlocksDTO
        super().__init__(
            ContentBlocks,
            self.dto_class,
            fetch_on_init_limit,
            fetch_on_init_with_warnings_off,
        )

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, content_blocks):
        pass

    async def create_content_blocks(self, **data):
        return await self.create_item(**data)

    async def delete_content_blocks(self, id):
        return await self.delete_item(id)

    async def get_content_blocks_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_content_blocks_by_id(self, id):
        return await self.load_by_id(id)

    async def load_content_blocks(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_content_blocks(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_content_block(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_content_block(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_content_blocks_with_shortcut_categories(self, id):
        return await self.get_item_with_related(id, "shortcut_categories")

    async def get_content_block_with_shortcut_categories(self):
        return await self.get_items_with_related("shortcut_categories")

    async def load_content_block_by_category_id(self, category_id):
        return await self.load_items(category_id=category_id)

    async def filter_content_block_by_category_id(self, category_id):
        return await self.filter_items(category_id=category_id)

    async def load_content_block_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_content_blocks_ids(self):
        return self.active_item_ids


class ContentBlocksManager(ContentBlocksBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ContentBlocksManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def get_template_text(self, id_or_block_id: str):
        if is_valid_uuid(id_or_block_id):
            block = await self.add_active_by_id_or_not(id_or_block_id)
            if block:
                return block.template
            return None
        else:
            models = await self.load_items(block_id=id_or_block_id)
            if models:
                return models[0].template  # Return the first match
            return None


content_blocks_manager_instance = None


def get_content_blocks_manager():
    global content_blocks_manager_instance
    if content_blocks_manager_instance is None:
        content_blocks_manager_instance = ContentBlocksManager()
    return content_blocks_manager_instance


if __name__ == "__main__":
    import asyncio
    from matrx_utils import clear_terminal

    clear_terminal()
    block = asyncio.run(get_content_blocks_manager().get_template_text("flashcards"))
    print(block)
