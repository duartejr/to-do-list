from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from datetime import timedelta


class Interrupt(Exception):
    pass


class ToDoList:
    def __init__(self, database):
        engine = create_engine("sqlite:///{}".format(database))
        Base = declarative_base()

        class Task(Base):
            __tablename__ = "task"
            id = Column(Integer, primary_key=True)
            task = Column(String)
            deadline = Column(Date, default=datetime.today())

            def repr(self):
                return self.task

        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        self.session = session
        self.Task = Task

    def add_task(self):
        task = input("\nEnter task\n")
        dead_line = datetime.strptime(input("Enter deadline\n"), '%Y-%m-%d')
        new_row = self.Task(task=task, deadline=dead_line)
        self.session.add(new_row)
        self.session.commit()
        print("The task has been added!\n")

    def get_tasks(self, date):
        tasks = self.session.query(self.Task).filter(self.Task.deadline == date).all()
        rows = self.session.query(self.Task).count()
        list_tasks = []
        if rows != 0:
            for task in tasks:
                list_tasks.append(task.task)
            return list_tasks
        return 0

    def exit(self):
        raise Interrupt

    def print_tasks(self, date):
        tasks = self.get_tasks(date)
        n = 1
        if tasks:
            for task in tasks:
                print(f'{n}. {task}')
                n += 1
            if n == 1:
                print("Nothing to do!\n")
            else:
                print("")
        else:
            print("Nothing to do!\n")

    def today_tasks(self):
        today = datetime.today().date()
        print("\nToday {}:".format(datetime.strftime(today, '%d %b')))
        self.print_tasks(today)
    
    def week_tasks(self):
        today = datetime.today().date()
        weekday = (today.weekday() + 1) % 7
        dates = [today + timedelta(days=i) for i in range(0 - weekday,
                                                          7 - weekday)]
        print("")
        for date in dates:
            print("{}:".format(datetime.strftime(date, "%A %d %b")))
            self.print_tasks(date)
            print("")
        pass

    def all_tasks(self):
        tasks = self.session.query(self.Task).all()
        n = 1
        if tasks:
            print("\nAll tasks:")
            for task in tasks:
                date = datetime.strftime(task.deadline, '%d %b')
                task = task.task
                print(f'{n}. {task}. {date}')
                n += 1
            print("")
        else:
            print('Nothing to do!\n')

    def missed_tasks(self):
        today = datetime.today().date()
        rows = self.session.query(self.Task).filter(self.Task.deadline < today).order_by(self.Task.deadline)
        n = 1
        if rows:
            print("\nMissed tasks:")
            for task in rows:
                date = datetime.strftime(task.deadline, '%d %b')
                task = task.task
                print(f'{n}. {task}. {date}')
                n += 1
            print("")
        else:
            print('Nothing is missed!\n')

    def delete_tasks(self):
        tasks = self.session.query(self.Task).order_by(self.Task.deadline).all()
        n = 1
        if tasks:
            print("\nChose the number of the task you want to delete:")
            for task in tasks:
                date = datetime.strftime(task.deadline, '%d %b')
                task = task.task
                print(f'{n}. {task} {date}')
                n += 1
            print("")

            n = int(input())
            specific_row = tasks[n-1]
            self.session.delete(specific_row)
            self.session.commit()
            print("The task has been deleted!\n")
        else:
            print("Nothing to delete!\n")

    def menu(self):
        actions = {"0": self.exit, "1": self.today_tasks, "2": self.week_tasks,
                   "3": self.all_tasks, "4": self.missed_tasks,
                   "5": self.add_task, "6": self.delete_tasks}
        print("1) Today's tasks\n2) Week's tasks\n3) All tasks\n4) Missed "
              "tasks\n5) Add task\n6) Delete task\n0) Exit")
        choice = input()
        actions[choice]()


def main():
    while True:
        to_do = ToDoList("todo.db")
        try:
            to_do.menu()
        except Interrupt:
            break
    print("Bye!")


if __name__ == "__main__":
    main()
