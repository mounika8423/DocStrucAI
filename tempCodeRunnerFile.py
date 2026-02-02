import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
key=os.getenv("OPENAI_API_KEY")

message="Hi, This is my first project using AI"
messages=[{"role":"user","content":message}]
openai=OpenAI()
response=openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages
)
response=openai.chat.completions.create(model="gpt-5-nano",messages=messages)
print(response)