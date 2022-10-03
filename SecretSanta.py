from __future__ import print_function

import base64
from email.message import EmailMessage

import google.auth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv, random

SCOPES = ['https://mail.google.com']

def read_file(filename):
    dictionary = {}
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')#Parse standard comma delimited csv file nothing fancy
        for row in readCSV: # row[n] reads the nth column of the current row.
            name = row[0]
            email = row[1]
            dictionary[name] = email
        return dictionary

def save_to(dictionary, filename):
    with open(filename, 'w', newline='') as csvfile:
        writeCSV = csv.writer(csvfile, delimiter=' ')
        for key in dictionary.keys():
            writeCSV.writerow({(key, dictionary[key])})

def send_email(recipient, rando, rando_email):
    print("Sending email to " + rando_email)
    
    email = """

    Hello %s,
    You have been selected to participate in this year's  Secret Santa!
    Your giftee is %s!
    
    """ % (rando, recipient)

    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(email)

        message['To'] = rando_email
        message['From'] = 'email@gmail.com'
        message['Subject'] = 'Secret Santa 2022'

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message
    
    

def main():
    random.seed()#Since no seed is entered, system time will be used.

    try:
        file = read_file('users2022.csv') #Read csv and return dictionary with users name as the key.
    except IOError as e:
        print ("Error opening file: %s" % str(e))
        return False

    users = file.keys() #Set array of users from the keys.
    randos = random.sample(users, len(users)) #Duplicate and shuffle the list.
    ss_list = {}
    
    for user in users: #Pair a user with a rando
        rando = random.choice(randos)
        if user == rando: # if they are the same, try again.
            while user == rando:
                print("Same person, try again\n")
                rando = random.choice(randos)
        ss_list[rando] = user     
        send_email(user,rando, file.get(rando)) #Pass info to email gifter with giftee info.
        del randos[randos.index(rando)] # remove rando from randos so they are not selected again.
    
    save_to(ss_list,'SecretSanta.csv')

main()