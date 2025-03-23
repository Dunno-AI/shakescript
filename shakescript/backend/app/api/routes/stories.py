from fastapi import APIRouter
from ...services.db_service import get_db
from ...services.ai_service import genai
from ...models.schemas import Prompt

router = APIRouter()

@router.get("/test-supabase")
def test_supabase():
    supabase = get_db()
    try:
        response = supabase.table("stories").select("*").execute()
        return {
            "status": "success",
            "data": response.data
        }
    except Exception as e:
        return {"error": str(e)}



@router.post("/ai")
def ai(request: Prompt):
    model = genai()
    response = model.generate_content(request.prompt)
    return {"response": response.text}

    



