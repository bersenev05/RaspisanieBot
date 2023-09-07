from fnmatch import fnmatch

raspisanie={}
#kurs/group

all_group={}
group = {}
file = []

system=["1kurs.csv", "2kurs.csv", "3kurs.csv", "4kurs.csv"]

def create_file(name):
    f = open(name, encoding="cp866")
    kray = 0
    for i in f:
        kray += 1
        if kray == 442:
            break
        file.append(list(map(str, i.split(";"))))

    for stroka in file:
        stolb = 0
        for element in stroka:
            if fnmatch(str(element), "КИ23*") == True:
                name = element.split()
                if len(name) > 1:
                    group[str(element.split()[0]) + "/" + str(element.split()[1][1])] = stolb + 3
                else:
                    group[str(element.split()[0])] = stolb + 3
                stolb += 1

def create_raspisanie(group_name):
    day = "x"
    para = "x"
    chetnost = "x"
    raspisanie={}
    nedelya=""

    for stroka in range(8, len(file)):

        time = file[stroka][:3]
        group_info = file[stroka][group[group_name]]

        if time[0] != day and time[0] != '':
            day = time[0]
            raspisanie[str(day)]={}

        if time[1] != para and time[1] != '':
            para = time[1]
            raspisanie[str(day)][str(para)] = {}

        if time[2] != chetnost and time[2] != '':
            chetnost = time[2]
            if chetnost=="1":
                nedelya="Нечётная неделя"
            else:
                nedelya="Чётная неделя"
            raspisanie[str(day)][str(para)][nedelya]=[]

        if group_info!="":
            raspisanie[day][para][nedelya].append(group_info)

    return raspisanie








create_file()
print(create_raspisanie("КИ23-11б/1"))

a={'Понедельник':

       {'8.30 - 10.05':
            {'Нечётная неделя': ['История России', 'Терскова А.А.', 'пр. занятие', 'ЭИОС', 'https://e.sfu-kras.ru/course/view.php?id=36628', 'асинхронно'],
             'Чётная неделя': []},

        '10.15 - 11.50':
            {'Нечётная неделя': ['Физическая культура и спорт', 'Вашко В.А.', 'пр. занятие', 'ЭИОС', 'https://e.sfu-kras.ru/course/view.php?id=32801', 'асинхронно'],
             'Чётная неделя': []},

        '12.00 - 13.35':
            {'Нечётная неделя': [],
             'Чётная неделя': ['Основы программирования', 'Раскина А.В.', 'лекция', 'Корпус №14', '34-14', 'синхронно']},

        '14.10 - 15.45':
            {'Нечётная неделя': [],
             'Чётная неделя': ['Информатика', 'Тушко Т.А.', 'лекция', 'Корпус №14', '34-14', 'синхронно']},

        '15.55 - 17.30':
            {'Нечётная неделя': [],
             'Чётная неделя': []},

        '17.40 - 19.15':
            {'Нечётная неделя': [],
             'Чётная неделя': []}}

   }
