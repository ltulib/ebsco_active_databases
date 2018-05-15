# Ebsco, EDS active databases

This is a small script to auto-create an active database list from Ebsco EDS.
It's checking for new mail sent from "auto-response@ebsco-gss.net" once a day.
When Ebsco has sent a new mail, the script download the attachments and creates 
an index.html file from it. All mails are marked as read.
 
When we get an error or have successfully created a new line is written to the log file.
 
At LTU we are using an iframe within our CMS to show the database list.

Best

Magnus Pettersson

magnus.pettersson@ltu.se
Librarian, Information Resources, Publishing and Systems
Luleå University of Technology


### Script running on:
 - Mac OS X (High Sierra) 
 - Debian 9
 - Not tried Windows.

### Dependencies:
- Python2.7
    - Modules are installed by default.
- Cron
- mail address which supports imap and SSL. No need to allow the address to send mail.
- write access to:
  - /opt/script/ebscomail/
  - /var/www/databases/index.html


### Install:

**Debian:**
```bash
apt update
apt install python2.7 cron -Y

useradd -m -d /opt/scripts/ebscomail ebscomail
usermod -a -G www-data ebscomail

# upload mail.py script to server and:
chmod ebscomail:ebscomail /opt/scripts/ebscomail/mail.py chmod 755 /opt/scripts/ebscomail/mail.py

mkdir /var/www/databases
chmod 755 /var/www/databases
  
cd /var/www/databases
touch index.html main.css
chmod 744 index.html main.css
 
chown -R ebscomail:www-data /var/www/databases
```

**crontab -e**
```bash
0 4 * * * /usr/bin/python /opt/script/ebscomail/mail.py >/dev/null 2>&1
```

**Try script:**
```bash
python /opt/ebscomail/mail.py
```

