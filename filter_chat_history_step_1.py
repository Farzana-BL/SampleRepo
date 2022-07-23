from config.database import db
from logger import logger
from datetime import datetime
import sys

log = logger.logger_init('filtered_chat_history_step_1')


class MyTrackerStore:

    def __init__(self) -> None:
        try:
            self.all_conversation_data = db.conversations.find()

        except:
            exception_type, _, exception_traceback = sys.exc_info()       
            line_number = exception_traceback.tb_lineno
            log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}")


    def check_timestamp(self,timestamp):
        """
            Description:
                This function is used to find the date difference based on the timestamps of conversations.
            Parameters:
                Timestamp: The timestamp of each conversation.
                Self object as a parameter.
            Return:
                Returns the date difference.
        """
        date_string_from_timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # To find the current date
        current_date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # convert string to date object
        date_from_timestamp = datetime.strptime(date_string_from_timestamp, "%Y-%m-%d %H:%M:%S").date()

        current_date = datetime.strptime(current_date_string, "%Y-%m-%d %H:%M:%S").date()

        # difference between dates in timedelta
        delta = current_date - date_from_timestamp
        return delta.days


    def conversation_filtering(self):
        """
            Description:
                This function is used to filter the conversation on the basis of different parameters.
            Parameters:
                Self object as a parameter.
            Return:
                Returns sender list containing unique sender id's along with their filtered data.
        """
        sender_list = []

        # Iterating through conversations.
        for conversation in self.all_conversation_data:
            chat_data = []
            distinct_event = {}
            sender_dict = {}
            event_data = conversation['events']
            
            # Iterating through events.
            for index in event_data:            
                if index.get('name')=='action_session_start':
                    
                    # Calling check_timestamp function to calculate the difference in date.
                    date_diff = self.check_timestamp(index['timestamp'])
                    continue
                # Checking for yesterday's data.
                if date_diff == 1:

                    # Checking if the event is equal to user.
                    if index['event']=='user':

                            # creating 'distinct_event' dictionary for storing the distinct events(user,bot,action).
                            distinct_event = {"user":index['event'],
                                            "timestamp":index['timestamp'],
                                            "user_text":index['text'],
                                            "intent":index['parse_data']['intent']['name']}

                            chat_data.append(distinct_event)

                    # Checking if the event is equal to bot.
                    elif index['event']=='bot':
                        buttons_list = []
                        data_dict = index['data']

                        # To check if the buttons are not null.
                        if data_dict['buttons']:
                            for p in data_dict['buttons']:
                                buttons_list.append(p['title'])
                            distinct_event = {"bot":index['event'],
                                            "timestamp":index['timestamp'],
                                            "bot_reply":index['text'],
                                            "buttons":buttons_list}

                        # To check if the buttons are null.
                        else:
                            distinct_event = {"bot":index['event'],
                                            "timestamp":index['timestamp'],
                                            "bot_reply":index['text']}

                        chat_data.append(distinct_event)

                    # Checking if the event is equal to action.
                    elif index['event']=='action':
                        action_names = ['action_session_start','action_listen']

                        # if the action names are not present in action_names.
                        if index['name'] not in action_names:
                            distinct_event = {"action":index['name'],
                                            "confidence":index['confidence']}

                            chat_data.append(distinct_event)

                # Checking if the chat_data list is empty or not
                if len(chat_data) != 0:
                    sender_dict = {"sender_id":conversation['sender_id'],"events":chat_data}
            
            # Checking if the sender_dict is not empty
            if sender_dict:
                sender_list.append(sender_dict)
        return sender_list


    def load_filtered_data(self,filtered_conversation_list):
        """
            Description:
                This function is used to load the filtered conversations
            Parameters:
                filtered_conversation_list: It contains unique sender id's along with their chat history.
                Self object as a parameter.
            Return:
                None
        """
        try:
            if len(filtered_conversation_list)!=0:
                db.filtered_conversations.insert_many(filtered_conversation_list)
                log.info(f"{len(filtered_conversation_list)} entries added to filtered_conversations collection")
            else:
                log.info(f"No Data Found")
        except:
            exception_type, _, exception_traceback = sys.exc_info()       
            line_number = exception_traceback.tb_lineno
            log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}")

                
def main():
    """
        Description:
            This function is used to call conversation_filtering and load_filtered_data functions.
        Parameters:
            None.
        Return:
            None.
    """
    tracker_store = MyTrackerStore()
    filtered_conversation_list = tracker_store.conversation_filtering()
    tracker_store.load_filtered_data(filtered_conversation_list)


if __name__ == "__main__":
    main()
