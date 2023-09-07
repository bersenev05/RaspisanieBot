
user_base = {}

async def client_info(id):
    message = ""
    id = str(id)

    if str(id) in user_base:

        for i in user_base[id]:

            if i == "id":
                message += f"<b>{i}:</b> <code>{user_base[id][str(i)]}</code>\n\n"

            elif i == "cjm":
                s = 0
                message += f"<b>{i}:</b>\n"
                message += "\n<b>           CJM_FILE.TXT...</b>\n"
                for j in user_base[id]["cjm"]:
                    s += 1
                    if (len(user_base[id]["cjm"]) - 10) <= s <= len(user_base[id]["cjm"]):
                        message += j + "\n"
                message += "\n"

            else:
                message += f"<b>{i}:</b> {user_base[id][str(i)]}\n"
    else:
        message = "в базе пусто"
    return message


async def user_file():
    system_file = open("system_file.txt", "w+")
    system_file.write(str(user_base))
    system_file.close()

    id_file = open("id_file.txt", "w+")
    for i in user_base:
        id_file.write(str(user_base[str(i)]["id"]) + "\n")
    id_file.close()

    username_file = open("username_file.txt", "w+")
    for i in user_base:
        username_file.write(str(user_base[str(i)]["username"]) + "\n")
    username_file.close()

    cjm_file = open("cjm_file.txt", "w+")
    for i in user_base:
        cjm_file.write(str(user_base[str(i)]["username"]) + "\n")
        cjm_file.write(str(user_base[str(i)]["id"]) + "\n")

        if "city" in user_base[str(i)]:
            cjm_file.write(str(user_base[str(i)]["city"]) + "\n")

        for j in user_base[str(i)]["cjm"]:
            cjm_file.write(str(j).replace("<b>", "").replace("</b>", "") + "\n")
        cjm_file.write("\n")
    cjm_file.close()


async def add_base(dictionary):
    for i in dictionary:

        if str(i) not in user_base:
            user_base[str(i)] = {}

            for j in dictionary[str(i)]:
                user_base[str(i)][j] = dictionary[i][j]
