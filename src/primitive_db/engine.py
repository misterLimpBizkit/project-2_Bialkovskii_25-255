import prompt
def welcome():
    '''
    Выводит приветствие и справку
    '''
    print("Добро пожаловать в DB-проект!")
    print("Доступные команды: 'help', 'exit'")
    while True:
        answer = prompt.string('Введите команду: ').strip().lower()
        if answer == 'exit':
            break
        if answer == 'help':
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            print('Неизвестная команда')
    
        