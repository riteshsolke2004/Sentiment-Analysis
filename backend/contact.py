# from fastapi import APIRouter, HTTPException
# from models import ContactForm
# from database import db
# from datetime import datetime

# router = APIRouter()

# @router.post("/contact")
# async def submit_contact(form: ContactForm):
#     data = form.dict()
#     data["created_at"] = datetime.utcnow()

#     try:
#         result = await db.contacts.insert_one(data)
#         if result.inserted_id:
#             return {"message": "Message submitted successfully"}
#         raise HTTPException(status_code=500, detail="Failed to save message")
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Internal server error")
