
import os
import sys
os.environ["DJANGO_SETTINGS_MODULE"] = "djangobot.settings"

import time
import couchdb

from logger.models import Message

def sleep():
    while True:
        time.sleep(1)

def transfer_messages(database, messages, chunk_size=5000):
    """
    Transfers the given `messages` to CouchDB in chunks specified by
    `chunk_size`. This allows calling code to be in control of how much
    memory is used during each iteration. Pretty important for running this
    on memory limited systems like a 512MB slice on SliceHost.
    """
    c = 0
    payload = []
    # select_related and values do not work together yet.
    for message in messages.select_related("channel").values().iterator():
        payload.append(couchdb.Document(**{
            "nickname": message["nickname"],
            "text": message["text"],
            "logged": message["logged"].strftime("%Y-%m-%d %H:%M:%S"),
            "is_action": message["is_action"],
            "is_blocked": message["is_blocked"],
        }))
        c += 1
        if not c % chunk_size:
            print "dumping payload [c=%d]" % c
            # we are ready to dump the payload on couchdb and clear it.
            database.update(payload)
            payload = []

def main():
    server = couchdb.Server("http://127.0.0.1:5984/")
    database = server.create("logger_messages")
    print "transferring messages to couchdb"
    transfer_messages(database, Message.objects.all())
    print "going to sleep for debugging purposes"
    try:
        sleep()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
