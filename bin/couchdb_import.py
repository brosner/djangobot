
import os
import sys
os.environ["DJANGO_SETTINGS_MODULE"] = "djangobot.settings"

import couchdb

from logger.models import Message

def chunkify(dataset, size=10):
    window = 0
    length = len(dataset)
    while window < length:
        yield dataset[window:window+size]
        window += size

def main():
    server = couchdb.Server("http://127.0.0.1:5984/")
    db = server["logger_messages"]
    count = 0
    messages = []
    print "building in-memory data"
    for message in Message.objects.all():
        messages.append(couchdb.Document(**{
            "nickname": message.nickname,
            "text": message.text,
            "logged": message.logged.strftime("%Y-%m-%d %H:%M:%S"),
            "is_action": message.is_action,
            "is_blocked": message.is_blocked,
        }))
    print "db.update"
    size = 20000
    for chunk in chunkify(messages, size):
        db.update(chunk)
        count += size
        sys.stdout.write("%d\r" % count)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
