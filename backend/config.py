import os


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Employee Management Portal API")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1200"))
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))

    BUSINESS_TIMEZONE = os.getenv("BUSINESS_TIMEZONE", "Asia/Kolkata")
    ATTENDANCE_LATE_PENALTY = float(os.getenv("ATTENDANCE_LATE_PENALTY", "1.0"))
    ATTENDANCE_ABSENCE_PENALTY = float(os.getenv("ATTENDANCE_ABSENCE_PENALTY", "10.0"))
    UNPLANNED_LEAVE_PENALTY = float(os.getenv("UNPLANNED_LEAVE_PENALTY", "10.0"))


settings = Settings()
