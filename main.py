from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase_client import supabase

app = FastAPI(
    title="Click2Pay API"
)


class AuthData(BaseModel):
    email:str
    password:str


class RegisterData(BaseModel):
    email:str
    password:str
    username:str
    fullname:str



# =====================
# REGISTER
# =====================

@app.post("/register")
async def register(data:RegisterData):

    try:

        result = supabase.auth.sign_up({
            "email":data.email,
            "password":data.password,
            "options":{
                "data":{
                    "username":data.username,
                    "full_name":data.fullname
                }
            }
        })


        return {
            "success":True,
            "message":"Akun berhasil dibuat",
            "user":result.user
        }


    except Exception as e:

        raise HTTPException(
            400,
            str(e)
        )



# =====================
# LOGIN EMAIL
# =====================

@app.post("/login")
async def login(data:AuthData):

    try:

        result = supabase.auth.sign_in_with_password({
            "email":data.email,
            "password":data.password
        })


        return {
            "success":True,
            "session":result.session,
            "user":result.user
        }


    except Exception:

        raise HTTPException(
            401,
            "Email atau password salah"
        )



# =====================
# FORGOT PASSWORD
# =====================

@app.post("/forgot-password")
async def forgot_password(data:dict):

    email=data.get("email")


    try:

        supabase.auth.reset_password_email(
            email,
            {
                "redirect_to":
                "https://click2pay.com/reset-password"
            }
        )


        return {
            "success":True,
            "message":
            "Link reset password dikirim"
        }


    except Exception as e:

        raise HTTPException(
            400,
            str(e)
        )
