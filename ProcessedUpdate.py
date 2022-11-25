import re
from datetime import datetime
from tkinter import SEL
from extraction import extract_wordle_number, extract_update_fields, extract_wordle_score
import Context
import os


class ProcessedUpdate:
    """
    A class used for an oject representation of a processed update message from Telegram
    
    Attributes
    ---------- 
    message -> str
        Returns an English written description of if it is todays wordle or if not, why it's is
        not today's wordle


    Methods
    ----------
    __init__(update: dict)
        Processes the raw telegram update (dict - type) object and assigns variables

    is_todays_wordle() -> Bool
        Has to be a function because it technically depends on the time of day, 
        If this was expressed as an attribute then the date could have changed between time of assignment 
        and time of validation
        
    """
    def __init__(self, update: dict):
        #TODO: list all self.attributes and assign defaults
        self.return_message = "This is an update "
        self.raw_update = update
        self.update_id = ""
        self.chat_id = 0
        self.chat_name = ""
        self.date = ""
        self.name = ""
        self.text = ""
        self.score = ""
        self.wordle_number = ""
        self.todays_wordle = False
        if self.is_text_message_update(update):
            self.return_message = self.return_message + "that is a text message "

            if self.is_from_groupchat(update):
                self.return_message = self.return_message + "from the correct groupchat "
                # Clean update for ease of use, see fields in extraction.py/extract_update_fields()
                mod_update = extract_update_fields(update)
                self.update_id = mod_update['update_id']
                self.chat_id = mod_update['chat_id']
                self.chat_name = mod_update['chat_name']
                self.date = mod_update['date']
                self.name = mod_update['name']
                self.text = mod_update['text']
                if self.is_todays_wordle():  
                    self.todays_wordle = True
                    self.return_message = self.return_message + "and is today's wordle. :)"
                    self.score = extract_wordle_score(self.text)

                    #TODO: Figure out handling non-submission (separate app? automic? some kindof scheduling mechanism for midnight that also submits the scoreboard, make sure to record if everyone  has submitted for the day so it will know not to run)
                    #TODO: Insert into spreadsheet
                else:
                    self.return_message = self.return_message + "so it's not today's wordle."
            else:
                self.return_message = self.return_message + "but it's not from the right chat."
        else:
            self.return_message = self.return_message + "but it's not the correct type."

    def __str__(self):
        return self.return_message


    def is_response_ok(response):
        return response["ok"]

    def is_reply_to(self, message_id):
        return "message" in self.raw_update and "reply_to_message" in self.raw_update['message'] and str(self.raw_update['message']['reply_to_message']['message_id']) == message_id

    def is_from_groupchat(self, update):
        """Only accepts message if it chat type is group, assumes message is text message"""
        #TODO: Also should check groupchat ID based on a config file or env variable
        return "chat" in update['message'] and update['message']['chat']['type'] == 'group' and str(update['message']['chat']['id']) == os.environ.get('CHAT_ID')

    def is_text_message_update(self, update):
        """Only accepts message type updates with text (not edits)"""
        return ( "message" in update and "text" in update["message"] )

    def is_todays_wordle(self):
        return_message_tail = "but it does not contain a correctly formatted wordle "
        if self.is_wordle_message():
            today = datetime.today().strftime("%Y-%m-%d")
            return_message_tail = f"but it was sent on {self.date} and today is {today} "
            if today == self.date:
                todays_wordle_number = Context.get_wordle_number(datetime.date(datetime.today()))
                self.wordle_number = extract_wordle_number(self.text)
                return_message_tail = f"but it is from wordle {self.wordle_number} and today's wordle is {todays_wordle_number} "
                if todays_wordle_number == self.wordle_number:
                    return True
        self.return_message = self.return_message + return_message_tail
        return False


    def is_wordle_message(self):
        pattern = re.compile("^Wordle [0-9]{3,4} [1-6,X]/6")
        return re.match(pattern, self.text)