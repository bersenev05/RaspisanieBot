from fnmatch import fnmatch

all_raspisanie = {}
all_groups = {}
groups_with_napr={}
system_files = ["1kurs.csv", "2kurs.csv", "3kurs.csv", "4kurs.csv"]


async def create_file(document):
    group = {}
    file = []
    napr_group=[]
    all_groups_with_napr = {}

    f = open(document, encoding="cp866")
    kurs = document[0]

    all_raspisanie[str(kurs)] = {}
    all_groups[str(kurs)] = []

    groups_with_napr[str(kurs)]={}

    kray = 0
    for i in f:
        kray += 1
        if kray == 442:
            break
        file.append(list(map(str, i.split(";"))))

    s = 0
    for stroka in file:
        s += 1
        if s==7:
            napr_group=stroka
            ff=0
            for i in stroka:
                ff+=1
                if i!="" and ff>3 and i!="\n":
                    all_groups_with_napr[i.split()[0]]=[]
            for element in range(len(napr_group)):
                if napr_group[element]=="" and napr_group[element]!="\n":
                    napr_group[element]=napr_group[element-1]

        if s == 8:
            k=0
            stolb = 0
            for element in stroka:
                if fnmatch(str(element), "КИ2*") == True:
                    name = element.split()
                    if len(name) > 1:
                        group[str(element.split()[0]) + "/" + str(element.split()[1][1])] = stolb + 3
                    else:
                        group[str(element.split()[0])] = stolb + 3
                    stolb += 1
                    k+=1

        if s > 8:
            break

    for i in group:
        if napr_group[group[i]]!="\n":
            all_groups_with_napr[napr_group[group[i]].split()[0]].append(i)

    for group_name in group:
        day = "x"
        para = "x"
        chetnost = "x"
        raspisanie = {}
        nedelya = ""

        for stroka in range(8, len(file)):

            time = file[stroka][:3]
            group_info = file[stroka][group[group_name]]

            if time[0] != day and time[0] != '':
                day = time[0]
                raspisanie[str(day)] = {}

            if time[1] != para and time[1] != '':
                para = time[1]
                raspisanie[str(day)][str(para)] = {}

            if time[2] != chetnost and time[2] != '':
                chetnost = time[2]
                if chetnost == "1":
                    nedelya = "Нечётная неделя"
                else:
                    nedelya = "Чётная неделя"
                raspisanie[str(day)][str(para)][nedelya] = []

            if group_info != "":
                raspisanie[day][para][nedelya].append(group_info)

        all_raspisanie[str(kurs)][str(group_name)] = raspisanie
        all_groups[str(kurs)].append(group_name)
        groups_with_napr[str(kurs)]=all_groups_with_napr
    f.close()


async def create_raspisanie():
    for i in system_files:
        await create_file(i)

async def create_timetable(kurs, group, nedelya):
    message=""
    raspisanie=all_raspisanie[kurs][group]

    for day in raspisanie:
        message+=f"<b>{day.upper()}</b>\n" \
                 f"------------\n"

        for time in raspisanie[day]:
            mesto=""
            if len(raspisanie[day][time][nedelya]) > 3:
                mesto = f"· {raspisanie[day][time][nedelya][3]} - {raspisanie[day][time][nedelya][4]}\n"
            if raspisanie[day][time][nedelya]!=[]:
                message+=f"🕘<b>{time}</b>\n" \
                         f"· <i>{raspisanie[day][time][nedelya][0]}</i>\n"\
                         f"{mesto}"
        message+="\n"
    return message


async def create_oneday_timetable(kurs,group,nedelya,day):

    raspisanie = all_raspisanie[kurs][group][day]

    message=f"<b>{day}</b> \n<i>[ {nedelya} ]</i>\n\n"

    for time in raspisanie:
        s=0
        if raspisanie[time][nedelya]!=[]:
            message += f"<b>🕘{time}</b>\n"
            for info in range(len(raspisanie[time][nedelya])):
                s+=1

                if s==1:
                    message += f"<b>📚{raspisanie[time][nedelya][info]}</b>\n"
                elif s==2:
                    message += f"<i>👩‍{raspisanie[time][nedelya][info]}</i>\n"

                else:
                    message+=f"<i>{raspisanie[time][nedelya][info]}</i>\n"

            message+="\n"

    return message


