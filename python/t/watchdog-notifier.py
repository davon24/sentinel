watchdog-notifier.py 
#!/usr/bin/env python2

__version__ = 'resin.watchdog.notifier.v1'

import sys, os, time, re, signal, atexit, logging, subprocess, threading, smtplib, socket
try: from email.mime.text import MIMEText
except ImportError:
    from email.MIMEText import MIMEText

def usage():
    print(sys.argv[0] + " /var/log/resin/watchdog-manager.log")
    sys.exit(0)

level = logging.INFO

MAIL_TO = ['ops@nationsinfocorp.com']
THIS_SERVER = socket.gethostname()
MAIL_FROM = THIS_SERVER + '@nationsinfocorp.com'
SMTP_SERVER = 'localhost'
SMTP_PORT = 25
SMTP_SSL = False
SMTP_AUTH = False
SMTP_USERNAME = ''
SMTP_PASSWORD = ''

hostname = os.uname()[1]
format = "%(asctime)s " + hostname + " %(filename)s %(levelname)s: %(message)s"
datefmt = "%b %d %H:%M:%S"
logging.basicConfig(level=level, format=format, datefmt=datefmt)
console = logging.StreamHandler(sys.stdout)
logging.getLogger(sys.argv[0]).addHandler(console)

def ticker():
    while (sigterm == False):
        processD()
        time.sleep(1)

def cleanup():
    logging.info("cleanup:")

def follow(cmd):
    try:
        process = subprocess.Popen(cmd, shell=False, stdin=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.STDOUT)
        while (process.returncode == None):
            line = process.stdout.readline()
            if not line or sigterm == True:
                break
            else:
                yield line
            sys.stdout.flush()
    except Exception as e:
        logging.debug("process exception " + str(e))

def send_notification(from_email, to_email, subject, message, smtp_server,
                      smtp_port, use_ssl, use_auth, smtp_user, smtp_pass):
    msg = MIMEText(message)

    msg['From'] = from_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] =  subject

    if(use_ssl):
        mailer = smtplib.SMTP_SSL(smtp_server, smtp_port)
    else:
        mailer = smtplib.SMTP(smtp_server, smtp_port)

    if(use_auth):
        mailer.login(smtp_user, smtp_pass)

    mailer.sendmail(from_email, to_email, msg.as_string())
    mailer.close()
    logging.info("mailer.sendmail: " + str(to_email))

def send_email(message=''):
    try:
        SUBJECT = 'Resin Restarted ' + THIS_SERVER
        send_notification(MAIL_FROM, MAIL_TO, SUBJECT,
                        str(message), SMTP_SERVER, SMTP_PORT, SMTP_SSL, SMTP_AUTH,
                        SMTP_USERNAME, SMTP_PASSWORD)
    except Exception as e:
        errorMessage = "Unable to send notification: " + str(e)
        logging.info(errorMessage)

def processD():
    for k,v in getD.items():
        logging.info(v)
        send_email(v)
        del getD[k] #print('poof ' + str(k) + ' ' + str(v))

sigterm = False
getD = {}

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print("File_Not_Found: " + filename)
            sys.exit(1)
    except IndexError:
        usage()

    atexit.register(cleanup) #python can't catch SIGKILL (kill -9)
    signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

    logging.info("Startup")

    #some log values to match/search for
    re_match1 = re.compile(r'Watchdog starting Resin',re.I)

    watcher = threading.Thread(target = ticker, name = "ticker")
    watcher.setDaemon(1)
    watcher.start()

    while (sigterm == False):
        try:
            #for line in follow(['tail', '-0', '-F',  filename]): #macos.tail
            for line in follow(['tail', '-n', '0', '-F',  filename]): #linux.tail
                try:
                    if re_match1.search(line):
                        getD[0] = line
                except TypeError as e:
                    errorMessage = "TypeError: " + str(e)
                    print(str(errorMessage + " " + str(line)))

        except (KeyboardInterrupt, SystemExit, Exception):
            sigterm = True
            watcher.join()
            cleanup()
            logging.info("Shutdown: " + str(sigterm))
            sys.exit(1)



