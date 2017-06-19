import sqlite3
import os.path
import sys

#fname = os.path.expanduser("~/Library/Messages/chat.db")
fname = "chatcopy.db"

class Message(object):
    def __init__(self, guid, is_from_me, text, rowid, attachments=None):
        self.guid = guid
        self.is_from_me = is_from_me
        self.text = text
        self.rowid = rowid
        self.attachments = attachments if attachments is not None else []


def export(contact):

    guid = 'iMessage;-;{}'.format(contact)

    db = sqlite3.connect(fname)
    cur = db.cursor()
    cur.execute("""SELECT chat.guid, message.is_from_me, message.text, message.rowid
    FROM message 
    INNER JOIN chat_handle_join USING (handle_id)
    INNER JOIN chat ON chat.rowid = chat_handle_join.chat_id
    WHERE chat.guid = ?
    ORDER BY message.rowid ASC""", (guid,))
    messages_rows = cur.fetchall()
    messages = {row[3]: Message(*row) for row in messages_rows}

    # print(messages)

    cur.execute("""
    SELECT chat.guid, attachment.filename, attachment.mime_type, message.rowid FROM attachment
    INNER JOIN message_attachment_join ON attachment.rowid = message_attachment_join.attachment_id
    INNER JOIN message ON message.rowid = message_attachment_join.message_id
    INNER JOIN chat_handle_join USING (handle_id)
    INNER JOIN chat ON chat.rowid = chat_handle_join.chat_id
    WHERE
        chat.guid = ?
        AND message.cache_has_attachments = 1""", (guid,))
    attachments_rows = cur.fetchall()

    for row in attachments_rows:
        (_, filename, mime_type, rowid) = row
        messages[rowid].attachments.append(row)

    # print(attachments_rows)

    # should not be an assert
    assert not ({x[-1] for x in attachments_rows} - messages.keys())

    return messages


if __name__ == '__main__':
    messages, attachments_rows = export(sys.argv[1])