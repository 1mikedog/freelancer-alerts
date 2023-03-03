class Database:
    def __init__(self, connection):
        self.connection = connection
        self.init()

    def init(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Jobs(
        Link TEXT
        )''')
        self.connection.commit()

    def getJob(self, link):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Jobs WHERE Link=%s", (link,))
        rows = cursor.fetchall()
        if len(rows) > 0:
            return rows[0]
        else:
            return []

    def saveJob(self, link):
        cursor = self.connection.cursor()
        sql = ''' INSERT INTO Jobs(Link)
          VALUES(%s) '''
        cursor.execute(sql, (link,))
        self.connection.commit()