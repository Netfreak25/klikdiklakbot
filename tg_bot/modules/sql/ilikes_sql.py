# New chat added -> setup permissions
import threading
import time
from sqlalchemy import Column, String, Boolean, Integer

from tg_bot.modules.sql import SESSION, BASE



class iLikes(BASE):
    __tablename__ = "ilikes"
    ilikes_id = Column(String(100), primary_key=True)
    found = Column(Integer, nullable=False)
    thanks = Column(Integer, nullable=False)
    notfound = Column(Integer, nullable=False)
    creator = Column(String(50), nullable=False)
    iliketype = Column(String(50), nullable=False)
    timestamp = Column(Integer, nullable=False)

    def __init__(self, ilikes_id, creator, iliketype):
        self.ilikes_id = str(ilikes_id)
        self.found = 0
        self.thanks = 0
        self.notfound = 0
        self.creator = creator
        self.iliketype = str(iliketype)
        self.timestamp = int(str(time.time()).split(".")[0])

    def __repr__(self):
        return "%s" % self.ilikes_id


class iLikes_Settings(BASE):
    __tablename__ = "ilikes_settings"
    chat_id = Column(String(100), primary_key=True)
    enabled = Column(Boolean, nullable=False)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)
        self.enabled = True

    def __repr__(self):
        return "%s" % self.chat_id



class iLikes_Clicks(BASE):
    __tablename__ = "ilikes_clicks"
    ilikes_click_id = Column(String(100), primary_key=True)
    found = Column(Integer, nullable=False)
    thanks = Column(Integer, nullable=False)
    notfound = Column(Integer, nullable=False)
    ilikes_id = Column(String(100), nullable=False)

    def __init__(self, ilikes_click_id, found, thanks, notfound, ilikes_id):
        self.ilikes_click_id = str(ilikes_click_id)
        self.found = str(found)
        self.thanks = str(thanks)
        self.notfound = str(notfound)
        self.ilikes_id = str(ilikes_id)

    def __repr__(self):
        return "%s" % self.ilikes_click_id




iLikes.__table__.create(checkfirst=True)
iLikes_Clicks.__table__.create(checkfirst=True)
iLikes_Settings.__table__.create(checkfirst=True)



PERM_LOCK = threading.RLock()
RESTR_LOCK = threading.RLock()

INSERTION_LOCK = threading.RLock()



def add_iLike(chat_id, msg_id, user_id, iliketype):
    with INSERTION_LOCK:
        new_ilikes_id = str(chat_id)+str(msg_id)
        ilikes_id = SESSION.query(iLikes).get(str(new_ilikes_id))
        if not ilikes_id:
            ilikes_id = iLikes(new_ilikes_id, user_id, str(iliketype))
            SESSION.add(ilikes_id)
            SESSION.commit()
            return True
        else:
            return False


def get_iLikes(chat_id, msg_id):
    with INSERTION_LOCK:
        try:
            with INSERTION_LOCK:
                new_ilikes_id = str(chat_id)+str(msg_id)
                ilikes_id = SESSION.query(iLikes).get(str(new_ilikes_id))
                found = ilikes_id.found
                thanks = ilikes_id.thanks
                notfound = ilikes_id.notfound
                user_id = ilikes_id.creator
                iliketype = ilikes_id.iliketype
                return(found, thanks, notfound, user_id, iliketype)
        except Exception as e:
            print(e)
            return False

def add_found_count(ilikes_id):
    with INSERTION_LOCK:
        ilikes_data = SESSION.query(iLikes).get(str(ilikes_id))
        ilikes_data.found = ilikes_data.found + 1
        SESSION.commit()

def del_found_count(ilikes_id):
        ilikes_data = SESSION.query(iLikes).get(str(ilikes_id))
        ilikes_data.found = ilikes_data.found - 1
        SESSION.commit()


def add_thanks_count(ilikes_id):
        ilikes_data = SESSION.query(iLikes).get(str(ilikes_id))
        ilikes_data.thanks = ilikes_data.thanks + 1
        SESSION.commit()
def del_thanks_count(ilikes_id):
        ilikes_data = SESSION.query(iLikes).get(str(ilikes_id))
        ilikes_data.thanks = ilikes_data.thanks - 1
        SESSION.commit()



def add_notfound_count(ilikes_id):
        ilikes_data = SESSION.query(iLikes).get(str(ilikes_id))
        ilikes_data.notfound = ilikes_data.notfound + 1
        SESSION.commit()

def del_notfound_count(ilikes_id):
        ilikes_data = SESSION.query(iLikes).get(str(ilikes_id))
        ilikes_data.notfound = ilikes_data.notfound - 1
        SESSION.commit()


def enable_ilikes(chat_id):
    with INSERTION_LOCK:
        ilikes_data = SESSION.query(iLikes_Settings).get(str(chat_id))
        ilikes_data.enabled = True
        SESSION.commit()

def disable_ilikes(chat_id):
    with INSERTION_LOCK:
        ilikes_data = SESSION.query(iLikes_Settings).get(str(chat_id))
        ilikes_data.enabled = False
        SESSION.commit()

def ilikes_enabled(chat_id):
    with INSERTION_LOCK:
        ilikes_data = SESSION.query(iLikes_Settings).get(str(chat_id))
        if not ilikes_data:
            return False
        else:
            return ilikes_data.enabled


def toggle_ilikes(chat_id):
    with INSERTION_LOCK:
        ilikes_data = SESSION.query(iLikes_Settings).get(str(chat_id))
        if not ilikes_data:
            ilike_setting = iLikes_Settings(chat_id)
            SESSION.add(ilike_setting)
            SESSION.commit()
            return True
        else:
            if ( ilikes_data.enabled == True ):
                disable_ilikes(chat_id)
                return False
            else:
                enable_ilikes(chat_id)
                return True

def delete_expired():
    with INSERTION_LOCK:
        hours = 24
        seconds = hours * 60 * 60
        timelimit = seconds
        cur_time = int(str(time.time()).split(".")[0])
        expired = SESSION.query(iLikes).filter(cur_time - iLikes.timestamp >= timelimit ).all()
        for ilike in expired:
            SESSION.delete(ilike)
            ilike_id = str(ilike)
            expired_clicks = SESSION.query(iLikes_Clicks).filter(iLikes_Clicks.ilikes_id == ilike_id ).all()
            for click in expired_clicks:
                SESSION.delete(click)
        SESSION.commit()

def add_iLike_Click(chat_id, msg_id, user_id, key, ilikestype):
    try:
        reply = ""
        if ( str(ilikestype) == "location"):
            tfound = "Fang bestätigt!"
            tfoundx = "Bestätigung zurück genommen!"
            tthanks = "Dein Dank wurde empfangen!"
            tthanksx = "Dank zurück genommen!"
            tnotfound = "Despawn bestätigt!"
            tnotfoundx = "Despawn zurück genommen!"
        else:
            tfound = "Like!"
            tfoundx = "Like zurück genommen!"
            tthanks = " !"
            tthanksx = " !"
            tnotfound = "Dislike!!"
            tnotfoundx = "Dislike zurück genommen!"

        with INSERTION_LOCK:
            new_ilikes_main_id = str(chat_id)+str(msg_id)
            new_ilikes_id = str(chat_id)+str(msg_id)+str(user_id)
            ilikes_id = SESSION.query(iLikes_Clicks).get(str(new_ilikes_id))
            if not ilikes_id:
                if ( str(key) == "thanks_key1"):
                    ilikes_id = iLikes_Clicks(new_ilikes_id, 1, 0, 0, new_ilikes_main_id)
                    add_found_count(new_ilikes_main_id)
                    reply = tfound
                if ( str(key) == "thanks_key2"):
                    ilikes_id = iLikes_Clicks(new_ilikes_id, 0, 1, 0, new_ilikes_main_id)
                    add_thanks_count(new_ilikes_main_id)
                    reply = tthanks
                if ( str(key) == "thanks_key3"):
                    ilikes_id = iLikes_Clicks(new_ilikes_id, 0, 0, 1, new_ilikes_main_id)
                    add_notfound_count(new_ilikes_main_id)
                    reply = tnotfound
                SESSION.add(ilikes_id)
                SESSION.commit()
                return reply
            else:

                new_ilikes_id = new_ilikes_main_id
                old_found = ilikes_id.found
                old_thanks = ilikes_id.thanks
                old_notfound = ilikes_id.notfound

                if ( str(key) == "thanks_key1" ):
                    found = 1
                    if ( old_found  == 1 ):
                        found = 0
                        del_found_count(new_ilikes_id)

                        reply = tfoundx
                    else:
                        add_found_count(new_ilikes_id)
                        if ( old_notfound  == 1 ):
                            notfound = 0
                            del_notfound_count(new_ilikes_id)
                            ilikes_id.notfound = notfound

                        reply = tfound

                    ilikes_id.found = found
                    SESSION.commit()

                elif ( str(key) == "thanks_key2" ):
                    thanks = 1
                    if old_thanks == 1:
                        thanks = 0
                        del_thanks_count(new_ilikes_id)
                        reply = tthanksx
                    else:
                        add_thanks_count(new_ilikes_id)
                        reply = tthanks
                    ilikes_id.thanks = thanks
                    SESSION.commit()

                elif ( str(key) == "thanks_key3" ):
                    notfound = 1
                    if old_notfound == 1:
                        notfound = 0
                        del_notfound_count(new_ilikes_id)
                        reply = tnotfoundx
                    else:
                        add_notfound_count(new_ilikes_id)
                        if ( old_found  == 1 ):
                            found = 0
                            del_found_count(new_ilikes_id)
                            ilikes_id.found = found

                        reply = tnotfound
                    ilikes_id.notfound = notfound

                    SESSION.commit()

                return reply
    except Exception as e:
        return "Es ist etwas schief gegangen!"


