from pyrogram import Client, filters
from pyrogram.errors import RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pydrive.auth import AuthenticationError, GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
import os

try:
    bot = Client(
        session_name="thunder_drive",
        api_id="1754216",
        api_hash="fd87630056c7f56e64c615d56641bfec",
        bot_token="1672130215:AAHN07ZYU27BbqEf2i3y1IxJ3G2pTnEateI"
    )

    gAuth = None

    @bot.on_message(filters.private & filters.incoming & filters.command(['auth']))
    def handle_auth(client, message):
        global gAuth
        
        if gAuth is None:
            gAuth = GoogleAuth()

        gAuth.LoadCredentialsFile("credentials.json")

        if gAuth.credentials is None:
            URL = gAuth.GetAuthUrl()
            message.reply_text(
                "1. Visit this URL\n2. Copy the Authorization Code after giving necessary permissions.\n3. Send the Authorization Code here",
                reply_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Authorization URL", url=URL)]]
                )
            )
        elif gAuth.access_token_expired:
            gAuth.Refresh()
            message.reply_text(
                "Google Drive Token Refreshed Successfully."
            )
            gAuth.SaveCredentialsFile("credentials.json")
            gAuth = None
        else:
            gAuth.Authorize()
            message.reply_text(
                "Google Drive Authorized Successfully."
            )
            gAuth.SaveCredentialsFile("credentials.json")
            gAuth = None
    
    @bot.on_message(filters.private & filters.incoming & filters.command(['token']))
    def handle_token(client, message):
        global gAuth
        token = message.command[1].strip()

        if len(token) == 62 and token[1] == "/":
            if gAuth is not None:
                try:
                    gAuth.Auth(token)
                    gAuth.SaveCredentialsFile("credentials.json")
                    message.reply_text(
                        "Authentication Successful !"
                    )
                    gAuth = None
                except AuthenticationError:
                    message.reply_text(
                        "Authentication Failed !"
                    )
            else:
                message.reply_text(
                    "No Authentication in progress ! Start an Authentication process first."
                )
        else:
            message.reply_text(
                "Invalid Token Provided.",
                quote = True
            )

    @bot.on_message(filters.private & filters.incoming & ~filters.text & filters.media) 
    def handle_media(client, message):
        gauth = GoogleAuth()

        gauth.LoadCredentialsFile("credentials.json")
        
        if gauth.access_token_expired:
            gauth.Refresh()

        if gauth.credentials is None:
            message.reply_text(
                "No Authentication Found! Authenticate Google Drive using 'auth' command.",
                quote = True
            )
        else:
            drive = GoogleDrive(gauth)
            status_msg = message.reply_text("Downloading file to server...", quote = True)
            file = bot.download_media(message)
            status_msg.edit("Uploading file to Google Drive...")
            driveFile = drive.CreateFile({
                'title': os.path.basename(file),
                'parents': [{
                    'kind': 'drive#fileLink',
                    'teamDriveId': '0AH0pUxFCGp6vUk9PVA',
                    'id': '1tzbV_qTs03TscQXLU3IBlLyM3xvMXN1V'
                }]
            })
            driveFile.SetContentFile(file)
            try:
                driveFile.Upload(param={'supportsTeamDrives': True})
                status_msg.edit(
                    "File successfully uploaded to Google Drive!"
                )
            except ApiRequestError:
                status_msg.edit("File Upload Failed!")

    bot.run()
except RPCError:
    pass
