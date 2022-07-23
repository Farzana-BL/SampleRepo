# Import modules
from config.database import db
from daily_email_html_content import contents_daily_analysis, contents_daywise_summary
from logger import logger
import sys
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import pandas as pd
import os


log = logger.logger_init('daily_email_report')


class DailyDataFetch:
   """DailyDataFetch Class is used to hold objects related to daily and daywise data"""

   def __init__(self) -> None:
      """DailyDataFetch Class Constructor to initialize the object"""
      try:
         self.daywise_summary_data = db.daywise_summary.find()

      except:
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}")    

   def load_daily_analysis_data(self, contents):
      """
         Description:
            This function is used to load daily data from daywise_summary collection.
         Parameters:
            contents: HTML and CSS contents for the daily analysis table.
            Self object as a parameter.
         Return:
            Returns the daily_analysis_contents.
      """
      try:
         daily_data = []

         self.collection_len = len(list(self.daywise_summary_data))-1

         #To iterate through saywise_summary collection
         for key,data in enumerate(db.daywise_summary.find()):

            #To get the latest chat data
            if key == self.collection_len:
                  col_name = list(data.keys())

                  #To fetch the column heading and data dynamically
                  for i,j in enumerate(col_name):
                     table = f"<tr><th>{col_name[i+1]}</th>\
                                   <th>{col_name[i+2]}</th>\
                                   <th>{col_name[i+3]}</th>\
                                   <th>{col_name[i+4]}</th></tr>"
                     daily_data.append(table)
                     a = "<tr><td>%s</td>"%data[col_name[i+1]]
                     daily_data.append(a)
                     b = "<td>%s</td>"%data[col_name[i+2]]
                     daily_data.append(b)
                     c = "<td>%s</td>"%data[col_name[i+3]]
                     daily_data.append(c)
                     d = "<td>%s</td></tr>"%data[col_name[i+4]]
                     daily_data.append(d)
                     break

         #To convert the daily_data list to string
         listToStr = ' '.join([str(elem) for elem in daily_data])

         daily_analysis_contents = contents%(listToStr)

      except:
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}") 

      return daily_analysis_contents


   def daywise_summary(self):
      """
         Description:
            This function is used to find the date of the latest chat data.
         Parameters:
            Self object as a parameter.
         Return:
            None.
      """
      try:
         for key,data in enumerate(db.daywise_summary.find()):
            if key == self.collection_len:
                  self.date = data["Date"]

      except:
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}")

   def load_daywise_summary(self,contents):
      """
         Description:
            This function is used to load daywise summary from daywise_user_analysis collection.
         Parameters:
            contents: HTML and CSS contents for the daywise summary table.
            Self object as a parameter.
         Return:
            Returns the daywise_summary_contents.
      """

      try:
         self.daywise_user_analysis = db.daywise_user_analysis.find({"Date":self.date})

      except:
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}")    

      try:
         daywise_data = []

         #To check whether the collection is empty or not for that particular date
         if len(list(self.daywise_user_analysis)) != 0:

            #To iterate through daywise_user_analysis collection
            for key,data in enumerate(db.daywise_user_analysis.find()):

               #To fetch the column name
               if key == 0:
                     col_name = list(data.keys())
                     for i,j in enumerate(col_name):
                        table = f"<tr><th>{col_name[i+1]}</th>\
                                      <th>{col_name[i+2]}</th>\
                                      <th>{col_name[i+3]}</th>\
                                      <th>{col_name[i+4]}</th>\
                                      <th>{col_name[i+5]}</th>\
                                      <th>{col_name[i+6]}</th>\
                                      <th>{col_name[i+7]}</th>\
                                      <th>{col_name[i+8]}</th></tr>"
                        daywise_data.append(table)
                        break

            #To fetch chat data within the particular date
            for key,data in enumerate(db.daywise_user_analysis.find({"Date":self.date})):
               col_name = list(data.keys())
               for i,j in enumerate(col_name):
                     daywise_data.append("<tr><td>%s</td>"%data[col_name[i+1]])
                     daywise_data.append("<td>%s</td>"%data[col_name[i+2]])
                     daywise_data.append("<td>%s</td>"%data[col_name[i+3]])
                     daywise_data.append("<td>%s</td>"%data[col_name[i+4]])
                     daywise_data.append("<td>%s</td>"%data[col_name[i+5]])
                     daywise_data.append("<td>%s</td>"%data[col_name[i+6]])
                     daywise_data.append("<td>%s</td>"%data[col_name[i+7]])
                     daywise_data.append("<td>%s</td></tr>"%data[col_name[i+8]])
                     break

            #To convert the daywise_data list to string
            listToStr = ' '.join([str(elem) for elem in daywise_data])

            #To apply html content to the fetched data
            daywise_summary_contents = contents%(listToStr)
      
         else:
            daywise_data.append("<h2>No Data Available for {}</h2>".format(self.date))

            listToStr = ' '.join([str(elem) for elem in daywise_data])

            daywise_summary_contents = contents%(listToStr)

      except:
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}") 

      return daywise_summary_contents


class DailyEmail:
   """DailyEmail Class is used to hold objects related to sending daily email"""


   def __init__(self)-> None:
      """DailyEmail Class Constructor to initialize the object"""
      try:
         self.email_sender = os.environ["EMAIL_SENDER"]
         self.email_password = os.environ["EMAIL_PASSWORD"]
         self.email_receiver = os.environ["EMAIL_RECEIVER"]
         self.email_host_server=os.environ["EMAIL_HOST_SERVER"]
         self.email_port=os.environ["EMAIL_PORT"]

      except:
         log.info("Email Not Sent")
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}")    


   def create_email(self,daily_contents, daywise_contents):
      """
         Description:
            This function is used to create the email for daily report.
         Parameters:
            daily_contents: It is the html object of daily analysis table.
            daywise_contents:It is the html object of daywise summary table.
            Self object as a parameter.
         Return:
            Returns the email string .
      """
      try:
         date_str = pd.Timestamp.today().strftime('%Y-%m-%d')

         email_message = MIMEMultipart()
         email_message['From'] = self.email_sender
         email_message['To'] = self.email_receiver
         email_message['Date'] = formatdate(localtime=True)
         email_message['Subject'] = f'Daily ChatBot-2.0 Report Summary - {date_str}'

         # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
         email_message.attach(MIMEText(daily_contents, "html"))
         email_message.attach(MIMEText(daywise_contents, "html"))

         # Convert it as a string
         email_string = email_message.as_string()

      except:
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}") 
   
      return email_string
   
   def send_email_message(self, email_message):
      """
         Description:
            This function is used to send the email for daily report.
         Parameters:
            email_message: It is a email string which we have to send in a mail.
            Self object as a parameter.
         Return:
            Returns the email string .
      """

      try:
         # Connect to the Gmail SMTP server and Send Email
         context = ssl.create_default_context()
         with smtplib.SMTP_SSL(self.email_host_server, self.email_port, context=context) as server:
            server.login(self.email_sender, self.email_password)
            server.sendmail(self.email_sender, self.email_receiver.split(","), email_message)
         log.info("Email Sent Successfully")

      except:
         log.info("Email Not Sent")
         exception_type,_, exception_traceback = sys.exc_info()       
         line_number = exception_traceback.tb_lineno
         log.exception(f"Exception type : {exception_type} \nError on line number : {line_number}")    


def main():
   """
      Description:
         This function is used to call other functions from DailyDataFetch and DailyEmail Class.
      Parameters:
         None.
      Return:
         None.
    """

   daily_data_fetch_obj = DailyDataFetch()
   daily_contents = daily_data_fetch_obj.load_daily_analysis_data(contents_daily_analysis)
   daily_data_fetch_obj.daywise_summary()
   daywise_contents = daily_data_fetch_obj.load_daywise_summary(contents_daywise_summary)
 
   daily_email_obj = DailyEmail()
   email_string = daily_email_obj.create_email(daily_contents, daywise_contents)
   daily_email_obj.send_email_message(email_string)


if __name__ == '__main__':
   main()
