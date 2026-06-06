from typing import Dict, Callable, Any, Optional
import logging
import asyncio

class SkillRegistry:
    """
    Registry to manage and trigger available skills for the AGI agent.
    """
    def __init__(self):
        self.skills: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}

    def register_skill(self, name: str, func: Callable, description: str):
        self.skills[name] = func
        self.descriptions[name] = description
        logging.info(f"Skill registered: {name}")

    def execute_skill(self, name: str, **kwargs) -> Any:
        if name not in self.skills:
            return f"Error: Skill '{name}' not found."
        try:
            func = self.skills[name]
            if asyncio.iscoroutinefunction(func):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    # We are in an active event loop and this method is synchronous.
                    # Since we cannot `await` it and `asyncio.run()` fails,
                    # we return an asyncio.Task object. The caller MUST be aware of it
                    # or the framework handling tools must await it if it's a coroutine.
                    return loop.create_task(func(**kwargs))
                else:
                    return asyncio.run(func(**kwargs))
            else:
                return func(**kwargs)
        except Exception as e:
            logging.error(f"Error executing skill {name}: {e}")
            return f"Error executing skill {name}: {e}"

    def get_skills_summary(self) -> str:
        summary = "Available Skills:\n"
        for name, desc in self.descriptions.items():
            summary += f"- {name}: {desc}\n"
        return summary
