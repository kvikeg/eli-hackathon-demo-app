import os
from pyexpat import model

from google import genai

# genai.configure(api_key="AIzaSyBf6vA8wVPJz9y_DoSzqD9OD2QPcSe7ifo")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# simple model call
def simple_call():
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents="Why is the sky green?"
    )
    print(response.text)

    # another option is generate_content_stream()
    # for stream in response:
    #     print(stream.text)
    #
    #


###########################################
# Chat:
def simple_chat():
    chat = client.chats.create(model="gemini-2.0-flash")
    while True:
        message = input(">")
        if message == "exit":
            break
        res = chat.send_message(message)
        print(res.text)


##########################################
# Multi-model
def multi_modal():
    uploaded_file = client.files.upload("path/to/file.txt")  # mp3, jpg, mp4, pdf
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=["question", uploaded_file]
    )
    print(response.text)


##############################################
# thinking modes
def thinking_mode():
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="What is the capital of France?",
        config={"thinking_config": {"thinking_budget": 1024, "include_thoughts": True}},
    )
    print(response.text)

    # if thoughts are included:
    for part in response.candidates[0].content.parts:
        if part.thought:
            print("Thought summary")
            print(part.text)


#####################################
# embeddings

result = client.models.embed_content(
    model="gemini-embedding-001", contents="What is the meaning of life?"
)

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="What is the meaning of life?",
    config=genai.types.EmbedContentConfig(output_dimensionality=768),
)
print(result.embeddings)


if __name__ == "__main__":
    thinking_mode()
