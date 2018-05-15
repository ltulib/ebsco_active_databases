# coding=utf-8

"""
Script created by Magnus Pettersson at Luleå University of Technology 2018

magnus.pettersson@ltu.se

"""

### Import modules ###
import datetime
import email
import imaplib
import json
import sys

### GLOBAL CONFIG ###
email_account = "vss-ebsco-database-u"
# email = ""
password = ""
mail_server = ""
mail_server_box = "inbox"
mail_status = "(UNSEEN)"
mail_from = "auto-response@ebsco-gss.net"

databases = "/opt/script/ebscomail/databases.json"
output_html = "/var/www/databases/index.html"
output_log = "/var/log/ebsco_mail_log.txt"

header = """
<link rel="stylesheet" href="main.css">
<div class="text-block">
"""

footer = """
</div>
"""


def connectToMailSerer():
    global mail_server, email_account, password, mail_server_box

    try:
        mail = imaplib.IMAP4_SSL(mail_server)
        mail.login(email_account, password)
        mail.list(mail_server)
        mail.select(mail_server_box)
        return mail
    except:
        msg = "Failed to connect to mail server"

    return False


def writeToLog(msg):
    global output_log

    print msg

    now = str(datetime.datetime.now())

    with open(output_log, "a") as file:
        file.write(now + " | " + msg + "\n")
        file.close()


def saveMailAttachements(original):
    global databases, output_log

    for part in original.walk():
        c_disp = part.get('Content-Disposition')
        c_type = part.get_content_type()
        if c_disp is not None and c_disp.startswith('attachment'):
            c_enc = part.get('Content-Transfer-Encoding')
            c_name = part.get_filename()

            try:
                c_content = part.get_payload().decode(c_enc)

                try:
                    with open(databases, 'wb') as fh:
                        try:
                            fh.write(c_content)
                            msg = '  Attachment %s extracted to %s' % (
                                c_name, databases)
                        except:
                            msg = '  Attachment %s extracted to %s' % (
                                c_name, databases)

                        writeToLog(msg)
                except:
                    msg = "Failed to load database.json file"
                    writeToLog(msg)
            except:
                msg = '  failed to retrieve attachements'
                writeToLog(msg)
                continue

def createHtmlOutput():
    global databases, output_html, header, footer
    data = json.load(open(databases))

    list = []
    for database in data['activeDatabases']:
        string = "<p>" + database + "</p>"
        list.append(string.encode('utf-8').strip())
        databaselist = ''.join(list)
        html = header + databaselist + footer

    try:
        file = open(output_html, "w")
        file.write(html)
        file.close()
        msg = '  index.html created at %s' % (output_html)
    except:
        msg = '  index.html failed to create'

    writeToLog(msg)


def retrieveAndProcessMail(new_mail, mail, num):
    print "\nProcessing mail: "
    new_mail = new_mail + 1
    typ, data = mail.fetch(num, '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            original = email.message_from_string(response_part[1])

            print "  " + original['From']
            # print original['Subject']
            typ, data = mail.store(num, '+FLAGS', '\\Seen')

            if original['from'] == mail_from:
                saveMailAttachements(original)
                createHtmlOutput()
            else:
                print("  No mail from Ebsco")

    return new_mail


def main():
    global mail_status
    new_mail = 0

    print("\nChecking for new Ebsco mail")

    mail = connectToMailSerer()

    if mail:
        retcode, messages = mail.search(None, mail_status)

        if retcode == 'OK':
            for num in messages[0].split():
                new_mail = retrieveAndProcessMail(new_mail, mail, num)
        else:
            msg = "Error retcode not OK"
            writeToLog(msg)

        mail.close()

        if new_mail == 0:
            print("No new mail\n")

        if new_mail > 0:
            print ("processed %i new mails" % new_mail)


if __name__ == '__main__':
    main()
