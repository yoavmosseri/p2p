import sqlite3

import json
# https://docs.python.org/2/library/sqlite3.html
# https://www.youtube.com/watch?v=U7nfe4adDw8


__author__ = 'yoav'


class Item(object):
    def __init__(self, name:str, size, signature:str, ip) -> None:
        self.name = name.lower()
        self.size = size
        self.signature= signature.lower()
        self.ip = ip
       







class ItemORM():
    def __init__(self,path):
        self.conn = None  # will store the DB connection
        self.cursor = None   # will store the DB connection cursor
        self.path = path

    def open_DB(self):
        """
        will open DB file and put value in:
        self.conn (need DB file name)
        and self.cursor
        """
        self.conn = sqlite3.connect(self.path)
        self.current = self.conn.cursor()

    def close_DB(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    # All read SQL


    def get_item_ip(self, name, size):
        self.open_DB()

        sql= f"SELECT ip FROM Items WHERE name = '{name}' AND size = {size};"
        res = self.current.execute(sql)
        
        res = res.fetchall()
        self.close_DB()
        return res

    def get_all_items(self):
        self.open_DB()

        sql= f"SELECT name,size FROM Items "
        res = self.current.execute(sql)
        
        res = res.fetchall()
        self.close_DB()
        return res


    # __________________________________________________________________________________________________________________
    # __________________________________________________________________________________________________________________
    # ______end of read start write ____________________________________________________________________________________
    # __________________________________________________________________________________________________________________
    # __________________________________________________________________________________________________________________
    # __________________________________________________________________________________________________________________

    # All write SQL

    

#id, name, size, signature, ip    

    def insert_item(self, i:Item):
        self.open_DB()


        sql = "INSERT INTO Items (name, size, signature, ip)"
        sql += f" VALUES ('{i.name}',{i.size},'{i.signature}','{i.ip}');"
        res = self.current.execute(sql)
       
        self.commit()
        self.close_DB()

        return True
        



def main_test():
    
    db = ItemORM('data\\items.db')
    i  = Item('bbb',888,'ajnfjne3243lkj','192.168.1.156')
    print(db.get_all_items())
    #data = db.get_all_players_in_a_team(1)
    #db.delete_player(1,24)
    #data = db.count_teams()
    #print(data)
    


if __name__ == "__main__":
    main_test()
