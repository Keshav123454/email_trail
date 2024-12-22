from fastapi import FastAPI, UploadFile, HTTPException
from typing import List, Dict
from email import message_from_binary_file
from email.utils import parsedate_to_datetime

app = FastAPI()

def parse_mail_with_attachment(msg):
    # msg = message_from_binary_file(file.file)
    email_data = []
    def extract_matadata(msg):
        return {
            "from": msg.get("From"),
            "to": msg.get("To"),
            "cc": msg.get("Cc"),
            "subject": msg.get("Subject"),
            "date": parsedate_to_datetime(msg.get("Date")).isoformat() if msg.get("Date") else None,
            "attachmentss":[],
            "contentss":[]
            # "message_id": msg.get("Message-ID"),
            # "in_reply_to": msg.get("In-Reply-To"),
            # "references": msg.get("References"),
        }


    if msg.is_multipart():
        attachment_data_list = []
        content_list = []

        for part in msg.walk():
            if part.get_content_type() in ["text/plain"]:#"text/html"
                content = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors='ignore') 
                # with open("test_.txt", "w") as file:
                #     file.write(content[:235])
                messages = split_thread(content[:250])
                with open("test_.txt", "w") as file:
                    for message in messages:
                        file.write(f'{message}')
                 
                for message in messages:
                    message = message.strip()[:15]
                    content_list.append(message)
                    email_data.append({**extract_matadata(msg), "content":message})

            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                attachment_data = {
                    "filename": filename,
                    "content_type": part.get_content_type(),
                    "size": len(part.get_payload(decode=True))
                }
                attachment_data_list.append(attachment_data)

        
        if len(content_list)>0 or len(attachment_data_list)>0:
            email_data.append({**extract_matadata(msg), "attachment_data": attachment_data_list, "content":list(reversed(content_list))})
            
    else:
        content = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", error="ignore")
        message = split_thread(content)
        for message in messages:
            message = message.strip()
            email_data.append({**extract_matadata(msg), "content":message})

    email_data.sort(key=lambda x: x["date"] if x["date"] else "")
    return email_data

def split_thread(content: str) -> List[str]:
    separators = [
        "-----Original Message-----",
        # "On .* wrote:",
        "On [\s\S]*? wrote:",
        "From: .*",
        "Sent: .*",
    ]
    import re
    pattern = "|".join(separators)
    # pattern = r"(On .+? wrote:)"
    message = re.split(pattern, content)
    print(content,pattern,'qqqq')
    print(message, len(message))
    return [msg.strip() for msg in message if msg.strip()]


@app.get('/')
def root():
    return {"message": "code run"}

# @app.post("/extract-email")
@app.post('/run/')
async def extract_emails(files: List[UploadFile]):

    extracted_data = []
    for file in files:
        if not file.filename.endswith(".eml"):
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

        msg = message_from_binary_file(file.file)
        print(type(msg))
        email_data = parse_mail_with_attachment(msg)
        extracted_data.append(email_data)
    return {"email": extracted_data}

