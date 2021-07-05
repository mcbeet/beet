"""
    Plugin that generates a advancement for this project.

    The aim of a project advancement is to replace installation messages in an easily viewable and non-obstructive way by putting them on a single advancement page.
"""

from typing import Any, Optional

from pydantic import BaseModel

from beet import Context, configurable
from beet.core.utils import TextComponent
from beet.library.data_pack import Advancement

AdvancementIcon = dict[str, Any]

class ProjectAdvancementOptions(BaseModel):
    icon: AdvancementIcon = {"item": "minecraft:apple"}
    author_namespace: Optional[str]
    author_description: str = ""
    author_skull_owner: Optional[str]
    project_namespace: Optional[str]
    project_advancement_path: Optional[str]

def beet_default(ctx: Context):
    ctx.require(project_advancement)

@configurable(validator=ProjectAdvancementOptions)
def project_advancement(ctx: Context, opts: ProjectAdvancementOptions):
    author_namespace = opts.author_namespace or ctx.project_author.lower()
    project_namespace = opts.project_namespace or ctx.project_id
    project_advancement_path = opts.project_advancement_path or f"{author_namespace}:{project_namespace}/installed"
    skull_owner = opts.author_skull_owner or ctx.project_author

    if not author_namespace:
        raise ValueError("Missing author namespace. Either author or author_namespace need to be configured")

    if not skull_owner:
        raise ValueError("Missing skull owner. Either author or author_skull_owner need to be configured")

    ctx.data["global:root"] = create_root_advancement()
    ctx.data[f"global:{author_namespace}"] = create_author_advancment(ctx.project_author, opts.author_description, skull_owner)
    ctx.data[project_advancement_path] = create_project_advancement(ctx.project_name, ctx.project_description, author_namespace, opts.icon)

def create_root_advancement():
    return Advancement({
        "display": {
            "title": "Installed Datapacks",
            "description": "",
            "icon": {
                "item": "minecraft:knowledge_book"
            },
            "background": "minecraft:textures/block/gray_concrete.png",
            "show_toast": False,
            "announce_to_chat": False
        },
        "criteria": {
            "trigger": {
                "trigger": "minecraft:tick"
            }
        }
    })

def create_author_advancment(author: TextComponent, author_description: TextComponent, skull_owner: str):
    return Advancement({
        "display": {
            "title": author,
            "description": author_description,
            "icon": {
                "item": "minecraft:player_head",
                "nbt": f"{{'SkullOwner': '{skull_owner}'}}"
            },
            "show_toast": False,
            "announce_to_chat": False
        },
        "parent": "global:root",
        "criteria": {
            "trigger": {
                "trigger": "minecraft:tick"
            }
        }
    })

def create_project_advancement(project_name: TextComponent, project_description: TextComponent, author_namespace: str, icon: AdvancementIcon):
    return Advancement({
        "display": {
            "title": project_name,
            "description": project_description,
            "icon": icon,
            "announce_to_chat": False,
            "show_toast": False
        },
        "parent": f"global:{author_namespace}",
        "criteria": {
            "trigger": {
                "trigger": "minecraft:tick"
            }
        }
    })
