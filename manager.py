import matplotlib.pyplot as plt
import sqlite3 as sql
import tkinter as tk
import api as gc
from tkinter import ttk
import threading
import time

class CryptoWindow:
    def __init__(self, master, db):
        self._master = master
        self._master.title("Crypto Manager - {0}".format(get_time(False)))
        self._master.resizable(False, False)
        self._master.bind("v", lambda x:self.__get_valuation())

        self.__create_layout()
        self.__create_items()
        self.__run_time()

        self.__investedView = None
        self.__recordView = None

        self.__cursor = db.cursor()
        self.__db = db
        self.__table = "crypto_table"
        self.__view_table()

    def __create_layout(self):
        self.__timeFrame = tk.Frame(self._master)
        self.__buttonFrame = tk.Frame(self._master)
        self.__widgetFrame = tk.Frame(self._master)
        self.__exitFrame = tk.Frame(self._master)

        self.__timeFrame.grid(row = 0, column = 0, columnspan = 1)
        self.__buttonFrame.grid(row = 1, column = 0)
        self.__widgetFrame.grid(row = 2, column = 0)
        self.__exitFrame.grid(row = 0, column = 0, sticky = "w")

    def __create_items(self):
        self.__timeLabel = tk.Label(self.__timeFrame, text = "TIME", font = ("TkDefaultFont", 14))
        self.__timeLabel.grid(row = 0, column = 0, columnspan = 2, sticky = "ew")

        self.__quitButton = tk.Button(self.__exitFrame, text = "QUIT", fg = "red", command = lambda:self.__close())
        self.__quitButton.grid(row = 0, column = 0, sticky = "w")

        self.__valuationButton = tk.Button(self.__buttonFrame, text = "Valuation", height = 2, width = 15, command = lambda:self.__get_valuation())
        self.__valuationButton.grid(row = 0, column = 1, padx = 3, pady = 3)
        self.__editInvestedButton = tk.Button(self.__buttonFrame, text = "Edit Invested", height = 2, width = 15, command = lambda:self.__edit_invested())
        self.__editInvestedButton.grid(row = 0, column = 2, padx = 3, pady = 3)
        self.__changeTableButton = tk.Button(self.__buttonFrame, text = "Change Table", height = 2, width = 15, command = lambda:self.__change_table())
        self.__changeTableButton.grid(row = 0, column = 3, padx = 3, pady = 3)

    def __close(self):
        if self.__tick is not None:
            self.__tick.cancel()
        self._master.destroy()

    def __run_time(self):
        try:
            self.__tick = threading.Timer(1.0, self.__run_time)
            self.__tick.start()
            time = get_time()
            self.__timeLabel["text"] = "{}".format(time[1])
            if self._master.title()[-10:] != time[0]:
                self._master.title("Crypto Manager - {0}".format(time[0]))
        except Exception as e:
            print("Time error:", e, end="! || ")
            if str(self.__tick)[17:24] == "started":
                print("Cancelling time tick.")
            else:
                print("Time tick cancelled.")
            self.__tick.cancel()

    ###TABLE FUNCTIONS###

    def __view_table(self):
        self.__columns = ("id", "symbol", "holdings")
        self.__tree = ttk.Treeview(self.__widgetFrame, columns=self.__columns[1:])
        i = 0
        for column in self.__columns:
            self.__tree.heading("#{0}".format(i), text = column)
            self.__tree.column("#{0}".format(i), stretch=tk.NO)
            i += 1
        self.__tree.grid(row=2, columnspan=3, sticky="nsew")
        self.__treeView = self.__tree
        self.__tree.bind("<Double-1>", self.__select_item)
        self.__selected = None
        
        sql = """SELECT * FROM {}""".format(self.__table)
        self.__cursor.execute(sql)
        data = self.__cursor.fetchall()
        for each in data:
            temp = []
            for i in range(1, len(each)):
                temp.append(each[i])
            values = tuple(temp)
            if values[1] != 0 or 1:
                self.__treeView.insert("", "end", text=each[0], values=values)

        self.__newButton = tk.Button(self.__widgetFrame, text = "New Record", height = 3, width = 25, font = ("TkDefaultFont", 10), command = lambda:self.__new_record())
        self.__editButton = tk.Button(self.__widgetFrame, text = "Edit Record", height = 3, width = 25, font = ("TkDefaultFont", 10), command = lambda:self.__edit_record())
        self.__removeButton = tk.Button(self.__widgetFrame, text = "Remove Record", height = 3, width = 25, font = ("TkDefaultFont", 10), command = lambda:self.__remove_record())
        self.__selectedLabel = tk.Label(self.__widgetFrame, text = " "*40)
        self.__tableLabel = tk.Label(self.__widgetFrame, text = self.__table)
        
        self.__newButton.grid(row = 0, column = 0, pady = 1)
        self.__editButton.grid(row = 0, column = 1, pady = 1)
        self.__removeButton.grid(row = 0, column = 2, pady = 1)
        self.__selectedLabel.grid(row = 1, column = 2, sticky = "w", pady = 2)
        self.__tableLabel.grid(row = 1, column = 0, sticky = "w", padx = 10)

    def __select_item(self, e):
        selected = self.__tree.focus()
        if len(selected) > 0:
            self.__selected = self.__tree.item(selected, "text")
            self.__selectedLabel.config(text= " "*40)
            self.__selectedLabel.config(text= "   Selected id: {0}".format(self.__selected))

    def __new_table(self):
        self.__change_table_view_close(1)
        
        self.__newTableView = tk.Tk()
        self.__newTableView.title("New Table")
        self.__newTableView.resizable(False, False)

        self.__labelFrame = tk.Frame(self.__newTableView)
        self.__inputFrame = tk.Frame(self.__newTableView)
        
        self.__labelFrame.grid(row = 0, column = 0)
        self.__inputFrame.grid(row = 0, column = 1)

        label = tk.Label(self.__labelFrame, text = "Enter name:")
        self.__newTableEntry = tk.Entry(self.__inputFrame)

        label.grid(row = 0, column = 0, sticky = "e", pady = 1)
        self.__newTableEntry.grid(row = 0, column = 1, sticky = "w", pady = 1)

        self.__cancel = tk.Button(self.__newTableView, text = "Cancel", height = 2, width = 20, command = lambda:self.__new_table_close(True))
        self.__cancel.grid(row = 1, column = 0)
        self.__confirm = tk.Button(self.__newTableView, text = "Confirm", height = 2, width = 20, command = lambda:self.__new_table_close())
        self.__confirm.grid(row = 1, column = 1)
        self.__newTableView.bind("<Return>", lambda x:self.__new_table_close())
        self.__newTableView.bind("<Escape>", lambda x:self.__new_table_close(1))

    def __new_table_close(self, cancel = False):
        if cancel:
            self.__newTableView.destroy()
            self.__newTableView = None
            self.__change_table()
        else:
            newVal = self.__newTableEntry.get().lower()

            sql1 = """CREATE TABLE {} (id varchar, symbol varchar, holdings float)""".format(newVal)
            sql2 = """INSERT INTO invested_table (table_name, invested)VALUES ({}, 0)""".format(newVal)

            self.__cursor.execute(sql)
            self.__cursor.execute(sql)
            self.__db.commit()
            self.__table = new_val
            self.__view_table()
                
            self._master.deiconify()
            self.__newTableView.destroy()
            self.__newTableView = None

    def __change_table(self):
        self.__changeTableView = tk.Tk()
        self.__changeTableView.title("Change Table")
        self.__changeTableView.resizable(False, False)

        self.__labelFrameC = tk.Frame(self.__changeTableView)
        self.__inputFrameC = tk.Frame(self.__changeTableView)
        
        self.__labelFrameC.grid(row = 0, column = 0)
        self.__inputFrameC.grid(row = 0, column = 1)

        self.__cursor.execute("SELECT name FROM sqlite_master")
        results = self.__cursor.fetchall()
        self.__tables = []
        for result in results:
            if result[0] not in ["sqlite_sequence", "invested_table"] and "sqlite_autoindex" not in result[0]:
                self.__tables.append(result[0])

        self.__changeTableVar = tk.StringVar(self.__changeTableView)
        self.__changeTableVar.set(self.__table)

        label = tk.Label(self.__labelFrameC, text = "Select table:").grid(row = 0, column = 0)
        dropdown = tk.OptionMenu(self.__inputFrameC, self.__changeTableVar, *self.__tables).grid(row = 0, column = 0)

        self.__newTableButton = tk.Button(self.__changeTableView, text = "New Table", height = 1, width = 20, command = lambda:self.__new_table())
        self.__newTableButton.grid(row = 1, column = 1)
        self.__cancel = tk.Button(self.__changeTableView, text = "Cancel", height = 2, width = 20, command = lambda:self.__change_table_view_close(True))
        self.__cancel.grid(row = 2, column = 0)
        self.__confirm = tk.Button(self.__changeTableView, text = "Confirm", height = 2, width = 20, command = lambda:self.__change_table_view_close())
        self.__confirm.grid(row = 2, column = 1)
        self.__changeTableView.bind("<Return>", lambda x:self.__change_table_view_close())
        self.__changeTableView.bind("<Escape>", lambda x:self.__change_table_view_close(1))
        
    def __change_table_view_close(self, cancel = False):
        if cancel:
            self.__changeTableView.destroy()
            self.__changeTableView = None
        else:
            self.__table = self.__changeTableVar.get()
            self.__selectedLabel.destroy()
            self.__tableLabel.destroy()
            self.__view_table()
                
            self._master.deiconify()
            self.__changeTableView.destroy()
            self.__changeTableView = None
            

    def __new_record(self):
        if self.__recordView != None:
            return
        self.__task = "new"
        self.__show_record_view("New Record")

    def __edit_record(self):
        if self.__selected is not None:
            if self.__recordView != None:
                return
            self.__task = "edit"
            self.__cursor.execute("""SELECT * FROM {} WHERE id='{}'""".format(self.__table, str(self.__selected)))
            data = self.__cursor.fetchone()
            self.__show_record_view("Record: {0}".format(self.__selected))
            for i in range(0, len(data)):
                    self.__inputs[i].insert(0, data[i])

    def __remove_record(self):
        self.__cursor.execute("""DELETE FROM {} WHERE id='{}'""".format(self.__table, str(self.__selected)))
        self.__db.commit()
        self.__view_table()

    def __show_record_view(self, title):
        self.__recordView = tk.Tk()
        self.__recordView.title(title)
        self.__recordView.resizable(False, False)

        self.__labelFrame = tk.Frame(self.__recordView)
        self.__inputFrame = tk.Frame(self.__recordView)
        
        self.__labelFrame.grid(row = 0, column = 0)
        self.__inputFrame.grid(row = 0, column = 1)

        labels = []
        self.__inputs = []
        i = 0
        for column in self.__columns:
            labels.append(tk.Label(self.__labelFrame, text = "{0}:".format(column)))
            self.__inputs.append(tk.Entry(self.__inputFrame))

            labels[i].grid(row = i, column = 0, sticky = "e", pady = 1)
            self.__inputs[i].grid(row = i, column = 1, sticky = "w", pady = 1)

            i += 1

        self.__cancel = tk.Button(self.__recordView, text = "Cancel", height = 2, width = 20, command = lambda:self.__record_view_close(True))
        self.__cancel.grid(row = 1, column = 0)
        self.__confirm = tk.Button(self.__recordView, text = "Confirm", height = 2, width = 20, command = lambda:self.__record_view_close())
        self.__confirm.grid(row = 1, column = 1)
        self.__recordView.bind("<Return>", lambda x:self.__record_view_close())
        self.__recordView.bind("<Escape>", lambda x:self.__record_view_close(1))

    def __unselect(self):
        self.__selectedLabel.config(text= " "*40)
        self.__selected = None
        
    def __record_view_close(self, cancel = False):
        if cancel:
            self.__recordView.destroy()
            self.__recordView = None
        else:
            values = []
            for i in range(0, len(self.__inputs)):
                if i == 0:
                    newVal = self.__inputs[i].get().lower()
                elif i == 1:
                    newVal = self.__inputs[i].get().upper()
                else:
                    newVal = self.__inputs[i].get()
                values.append(newVal)
            flag = False 
            for value in values:
                if "" == value:
                    flag = True
            if flag:
                print("Error: Empty value(s)")
                return
            else:
                if self.__task == "edit":
                    sql = """UPDATE {} SET """.format(self.__table)
                    for i in range(0, len(values)):
                        sql += self.__columns[i] + """ = '"""+str(values[i])+"""', """
                    sql = sql[:-2] + """ WHERE id='"""+str(self.__selected)+"""'"""
                elif self.__task == "new":
                    sql = """INSERT INTO {} (""".format(self.__table)
                    for i in range(0, len(self.__columns)):
                        sql += self.__columns[i] +""", """
                    sql = sql[:-2] + """) VALUES ('"""
                    for i in range(0, len(self.__columns)):
                        sql += str(values[i])+"""', '"""
                    sql = sql[:-4] + """')"""
                self.__cursor.execute(sql)
                self.__db.commit()
                self.__tableLabel.destroy()
                self.__view_table()
                
                self._master.deiconify()
                self.__recordView.destroy()
                self.__recordView = None
        if self.__task == "new" or not cancel:
            self.__unselect()

        ###TABLE FUNCTIONS END###

    def __get_valuation(self, currency = "gbp"):
        self.__cursor.execute("""SELECT id, symbol, holdings FROM {}""".format(self.__table))
        results = self.__cursor.fetchall()
        self.__cursor.execute("""SELECT invested FROM invested_table WHERE table_name = '{}'""".format(self.__table))
        invested = float(self.__cursor.fetchone()[0])
        total, totalR = 0, 0
        labels, sizes = [], []
        for crypto in results:
            if crypto[2] > 0:
                url = "https://api.coingecko.com/api/v3/coins/{}".format(crypto[0])
                data = gc.CoingeckoAPI(url).get_coingecko_data()["market_data"]
                price = data["current_price"][currency]
                value = price*crypto[2]
                valueR = round_(value)
                total += value
                totalR += valueR
                print("{0:>8} {1:^5} = £{2:<8.2f} >>  £{3:.2f}".format(crypto[2], crypto[1], value, valueR))
                labels.append(crypto[1])
                sizes.append(valueR)
            
        print("-----\nTotal Blockfolio Value: £{0:<7.2f} >>  £{1:.2f}".format(total, totalR))
        if invested != 0:
            print("Total Investment Made:  £{0}, P/L: {1}£{2:.2f} ({3:.1f}%)".format(invested, is_pos(total - invested), abs(total - invested), (total - invested)*100 / invested))
        print("@ {} on {}\n-----".format(get_time(1)[1], get_time(0)))

        try:
            plt.clf()
            patches, texts, autotexts = plt.pie(sizes, startangle=90, autopct="%.1f", counterclock=False)
            plt.legend(patches, labels, loc="best")
            plt.axis("equal")
            for text in autotexts:
                text.set_text("{}%".format(text.get_text()))
            plt.tight_layout()
            plt.show()
        except:
            pass

    def __edit_invested(self):
        if self.__investedView != None:
            return
        self.__investedView = tk.Tk()
        self.__investedView.title("Edit Invested")
        self.__investedView.resizable(False, False)

        currentLabel = tk.Label(self.__investedView, text = "Current:")
        currentLabel.grid(row = 0, column = 0)
        currentAmount = tk.Label(self.__investedView, text = self.__get_invested())
        currentAmount.grid(row = 0, column = 1)
        investedLabel = tk.Label(self.__investedView, text = "Invested:")
        investedLabel.grid(row = 1, column = 0)
        self.__investedEntry = tk.Entry(self.__investedView)
        self.__investedEntry.grid(row = 1, column = 1)

        cancelI = tk.Button(self.__investedView, text = "Cancel", height = 2, width = 20, command = lambda:self.__invested_view_close(True))
        cancelI.grid(row = 2, column = 0)
        confirmI = tk.Button(self.__investedView, text = "Confirm", height = 2, width = 20, command = lambda:self.__invested_view_close())
        confirmI.grid(row = 2, column = 1)
        self.__investedView.bind("<Return>", lambda x:self.__invested_view_close())
        self.__investedView.bind("<Escape>", lambda x:self.__invested_view_close(1))

    def __get_invested(self):
        self.__cursor.execute("SELECT invested FROM invested_table WHERE table_name = '{}'".format(self.__table))
        return int(self.__cursor.fetchone()[0])
    
    def __invested_view_close(self, cancel = False): #Closes record view
        if cancel:
            self.__investedView.destroy()
            self.__investedView = None
        else:
            value = self.__investedEntry.get()
            flag = False 
            if "" == value:
                flag = True
            if flag:
                print("Error: Empty value")
            else:
                if value[0] == "+" or value[0] == "-":
                    value = self.__get_invested() + int(str(value[0:]))
                sql = """UPDATE invested_table SET invested = '{}' WHERE table_name = '{}'""".format(str(value), self.__table)
                self.__cursor.execute(sql)
                self.__db.commit()
                
                self.__investedView.destroy()
                self.__investedView = None
                

def round_(value, to = .5):
    if (value % to) >= (to / 2):
        rounded = (value + to) - (value % to)
    else:
        rounded = value - (value % to)
    return rounded

def is_pos(value):
    if value < 0:
        return "-"
    else:
        return " "                   
        
def get_time(time_ = True):
    t = time.localtime()
    ts = [str(t[3]), str(t[4]), str(t[5]), str(t[2]), str(t[1]), str(t[0])]
    for i in range(5):
        if len(ts[i]) == 1:
            new = "0"+str(ts[i])
            ts[i] = new
            
    timeString = "{0}:{1}:{2}".format(ts[0], ts[1], ts[2])
    dateString = "{0}/{1}/{2}".format(ts[3], ts[4], ts[5])

    if time_:
        return dateString, timeString
    else:
        return dateString

def main():
    with sql.connect("data.db") as db:
        db_ = db
    
    root = tk.Tk()
    win = CryptoWindow(root, db_)
    win._master.mainloop()

if __name__ == "__main__":
    main()
