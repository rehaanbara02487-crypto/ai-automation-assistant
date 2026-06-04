import base64
from email.message import EmailMessage

from fastapi import HTTPException
from google.auth.exceptions import GoogleAuthError, RefreshError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import Settings


GMAIL_SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


class GmailService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_email(self, *, to: str, subject: str, body: str) -> dict[str, str]:
        if not self.settings.gmail_configured:
            raise HTTPException(
                status_code=503,
                detail="Gmail is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN.",
            )

        message = EmailMessage()
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        try:
            service = build("gmail", "v1", credentials=self._credentials(), cache_discovery=False)
            result = service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
        except RefreshError as exc:
            raise HTTPException(status_code=502, detail="Gmail OAuth refresh token is invalid or expired.") from exc
        except GoogleAuthError as exc:
            raise HTTPException(status_code=502, detail="Gmail OAuth authentication failed.") from exc
        except HttpError as exc:
            detail = getattr(exc, "reason", None) or "Gmail API request failed."
            raise HTTPException(status_code=502, detail=detail) from exc

        message_id = result.get("id")
        if not message_id:
            raise HTTPException(status_code=502, detail="Gmail accepted the request but did not return a message id.")

        return {"message_id": message_id}

    def _credentials(self) -> Credentials:
        return Credentials(
            token=None,
            refresh_token=self.settings.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.settings.google_client_id,
            client_secret=self.settings.google_client_secret,
            scopes=[GMAIL_SEND_SCOPE],
        )
