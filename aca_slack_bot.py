from cgitb import handler
import datetime
from email import contentmanager
import logging
import os

from dotenv import load_dotenv
from slack_bolt import App, Say
from slack_bolt.adapter.socket_mode import SocketModeHandler

import requests
import json
import time
import math

logging.basicConfig(level=logging.INFO)
load_dotenv()

SLACK_BOT_TOKEN = os.environ["Bot_User_OAuth_Token"]
SLACK_APP_TOKEN = os.environ["ACA_Slack_Bot_Token"]
NEWS_API_TOKEN = os.environ["News_API_Token"]
WEATHER_API_TOKEN = os.environ["Weather_API_Token"]

BMO = App(token=SLACK_BOT_TOKEN)

ISO_country_code = [
    {"code": "us", "country": "United State"},
    {"code": "ca", "country": "Canada"},
    {"code": "fr", "country": "France"},
    {"code": "tw", "country": "Taiwan"},
]

Topics = ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']

User_todo = {}
User_news_setting = {}
User_weather_setting = {}

@BMO.event("app_home_opened")
def update_home_tab(client, event, logger):
    current = math.floor(time.time())
    # print(event)
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Hi there :wave:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Great to see you here! My name is BMO, and I'm here to help you to stay up-to-date right here within Slack. These are just a few things which you will be able to do:\n"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                            "type": "mrkdwn",
                            "text": f":newspaper: Your daily digest, <!date^{current}^{{date}} at {{time}}|February 18th, 2014 at 6:39 AM PST>"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": get_news(event["user"])
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                            "type": "mrkdwn",
                            "text": f":umbrella_on_ground: Today’s weather"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": get_weather(event["user"])
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                            "type": "mrkdwn",
                            "text": f":ballot_box_with_check: To-do List"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": get_todo(event["user"])
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Thank you for installing BMO :hotdog: \n Before you can do all these amazing things, we need you to set up some information. Simply click the button below:"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                        "type": "plain_text",
                                        "text": "News Settings",
                                                "emoji": True
                                },
                                "action_id": "open_news_modal",
                                "value": "click_me_123"
                            },
                            {
                                "type": "button",
                                "text": {
                                        "type": "plain_text",
                                        "text": "Weather Settings",
                                                "emoji": True
                                },
                                "action_id": "open_weather_modal",
                                "value": "click_me_123"
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


def get_news(user_id):
    if user_id in User_news_setting:
        news = requests.get('https://newsapi.org/v2/top-headlines?country='+ User_news_setting[user_id]['country'] + '&category=' + User_news_setting[user_id]['topic'] + '&apiKey=' + NEWS_API_TOKEN)
        headlines = news.json()

        count = 0
        top_titles = []
        while count < 5:
            top_titles.append(str(count + 1) + '. ' + '<' + headlines['articles'][count]['url'] + '|' + headlines['articles'][count]['title'] + '>\n')
            count += 1

        return ('\n'.join(top_titles))        
    else:
        return ("Please complete news setting first.")


def get_weather(user_id):
    if user_id in User_weather_setting:
        weather = requests.get(
                    "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/" + User_weather_setting[user_id] + "?key=" + WEATHER_API_TOKEN)
        weather_json = weather.json()

        return ("Today's temperature for " + User_weather_setting[user_id] + " is " + str(weather_json['currentConditions']['temp']) + " fahrenheit.\n" + weather_json['description'])
    else:
        return ("Please complete weather setting first.")

@BMO.event("message")
def selected_message(message, say):
    if 'news' in message['text']:
        print(message)
        say(get_news(message['user']))

    if 'weather' in message['text']:
        say(get_weather(message['user']))

# Listen for a shortcut invocation


@BMO.action("open_news_modal")
def open_news_modal(ack, body, client):
    # Acknowledge the command request
    ack()
    user = body['user']['username']
    # Call views_open with the built-in client
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view={
            "type": "modal",
            "callback_id": "view_news_submission",
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "title": {
                "type": "plain_text",
                "text": "App menu",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Hi there, <@{user}>!* Select from the following items:"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":newspaper: *News Topics*\nChoose one topic you're interested in"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                                "type": "plain_text",
                                "text": "Select an item",
                                        "emoji": True
                        },
                        "action_id": "save_news_topic",
                        "options": list(map(lambda topic: {
                            "text": {
                                    "type": "plain_text",
                                    "text": topic,
                                    "emoji": True
                                },
                                "value": topic
                        }, Topics))
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":dart: *Country*\nChoose one loaction you're interested in"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True
                        },
                        "action_id": "save_news_country",
                        "options": list(map(lambda iso: {
                            "text": {
                                        "type": "plain_text",
                                        "text": iso["country"],
                                        "emoji": True
                                        },
                            "value": iso["code"]
                        }, ISO_country_code))
                    }
                }

            ]
        }
    )

@BMO.action("open_weather_modal")
def open_weather_modal(ack, body, client):
    # Acknowledge the command request
    ack()
    user = body['user']['username']
    # Call views_open with the built-in client
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view={
            "type": "modal",
            "callback_id": "view_weather_submission",
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "title": {
                "type": "plain_text",
                "text": "App menu",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Hi there, <@{user}>!* I need your zip code to get weather information."
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "save_weather_zip"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Please input your zip",
                        "emoji": True
                    }
                }
            ]
        }
    )


@BMO.action("save_news_topic")
@BMO.action("save_news_country")
def save_news_setting(ack, body, client):
    ack()
    User_id = body['user']['id']
    if User_id not in User_news_setting:
        User_news_setting[User_id] = {
            "topic": 0,
            "country": 0
        }
    Action_key = "topic" if body['actions'][0]['action_id'] == 'save_news_topic' else "country"
    User_news_setting[User_id][Action_key] = body['actions'][0]['selected_option']['value']

    print(User_news_setting)

@BMO.action("save_weather_zip")
@BMO.view("view_weather_submission")
@BMO.view("")
def save_weather_setting(ack, body, client):
    ack()
    User_id = body['user']['id']
    if User_id not in User_weather_setting:
        User_weather_setting[User_id] = 0
    value_id = list(body['view']['state']['values'].keys())[0]
    zip = body['view']['state']['values'][value_id]['save_weather_zip']['value']
    User_weather_setting[User_id] = zip
    print(User_weather_setting)


@BMO.event("app_mention")
def mention_handler(body, context, payload, options, say, event):
    user = body['event']['user']
    say(f"Hello <@{user}>! My name is BMO.\n" 
    "I’m here to provide you news and weather information. You can also write down to do list.\n\n" + 
    ":slack: Just heck out the following instruction!\n" +
    "• type word `news` to get today’s digest\n" +
    "• type word `weather` to get today’s weather\n" +
    "• type slash command `/bmo-todo + things you wanna complete`\n" +
    "   • `/bmo-todo-show` to show your to do list\n" +
    "   • `/bmo-todo-delete + number` to delete the task\n")

# @BMO.event("message")
# def message_handler(body, context, payload, options, say, event):
#     pass


@BMO.command("/bmo-todo")
def write_todo(ack, say, command):
    print(command)
    ack()
    if command['user_id'] in User_todo:
        User_todo[command['user_id']].append(command['text'])
    else:
        User_todo[command['user_id']] = [command['text']]
    say(f"\"{command['text']}\" is now in your to-do list. Check it on App Home or type `/bmo-todo-show`.")

def get_todo(user_id):
    if user_id in User_todo:
        result = ["Here is your todo task:"]
        count = 1
        for i in User_todo[user_id]:
            result.append(f"{count}. {i}")
            count += 1
        return ('\n'.join(result))
    else:
        return ("You don't have any to do for now.")

@BMO.command("/bmo-todo-show")
def show_todo(ack, say, command):
    ack()
    say(get_todo(command['user_id']))

@BMO.command("/bmo-todo-delete")
def delete_todo(ack, say, command):
    ack()
    idx = int(command['text']) - 1
    say(f"\"{User_todo[command['user_id']][idx]}\" is now removed from your to do.")
    del User_todo[command['user_id']][idx]

@BMO.view("view_news_submission")
def handle_view_submission(ack):
    ack()


if __name__ == "__main__":
    print(SLACK_APP_TOKEN)
    print(SLACK_BOT_TOKEN)
    handler = SocketModeHandler(BMO, SLACK_APP_TOKEN)
    handler.start()