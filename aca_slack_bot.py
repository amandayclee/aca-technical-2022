from cgitb import handler
import logging
import os

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(level=logging.INFO)
load_dotenv()

SLACK_BOT_TOKEN = os.environ["Bot_User_OAuth_Token"]
SLACK_APP_TOKEN = os.environ["ACA_Slack_Bot_Token"]

aca_slack_bot = App(token=SLACK_BOT_TOKEN)

@aca_slack_bot.event("app_mention")
def mention_handler(body, context, payload, options, say, event):
    say("Hello World!")

@aca_slack_bot.event("message")
def message_handler(body, context, payload, options, say, event):
    pass

if __name__ == "__main__":
    print(SLACK_APP_TOKEN)
    print(SLACK_BOT_TOKEN)
    handler = SocketModeHandler(aca_slack_bot, SLACK_APP_TOKEN)
    handler.start()

