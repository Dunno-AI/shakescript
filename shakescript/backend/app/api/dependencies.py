from app.services.story_service import StoryService

def get_story_service() -> StoryService:
    return StoryService()
