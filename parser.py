import requests
from fake_useragent import UserAgent
import json
import time
import csv

"""
ТЗ:
Для каждого студента из этих направлений найти соответствие, на какое направление он ещё собирается пойти, вывести его номер, сумму баллов, приоритет и есть ли согласие на зачисление.
Далее для каждого направления вывести студентов, которые выше меня и какие у них шансы на поступление в другое направление.
"""

direction_names = ['ИИБД','КИС','МКТ','КБЗ','РПИС']
direction_urls = [
    'https://www.dvfu.ru/bitrix/services/main/ajax.php?admissionCampaignType=Магистратура&financingSource=Бюджет&studyForm=Очная&trainingDirection=09.04.01%20-%20Информатика%20и%20вычислительная%20техника%20(Искусственный%20интеллект%20и%20большие%20данные%20(совместно%20с%20ПАО%20Сбербанк))%20&sortDirection=prioritet&enrolled=N&sendorig=N&topprior=N&toppriornoorig=N&approval=N&excludeBudgetEnrolled=N&contract=N&mode=class&c=dvfu%3Aadmission.spd&action=getStudents',
    'https://www.dvfu.ru/bitrix/services/main/ajax.php?admissionCampaignType=Магистратура&financingSource=Бюджет&studyForm=Очная&trainingDirection=09.04.03%20-%20Прикладная%20информатика%20(Корпоративные%20информационные%20системы%20(совместно%20с%20ПАО%20Сбербанк))%20&sortDirection=prioritet&enrolled=N&sendorig=N&topprior=N&toppriornoorig=N&approval=N&excludeBudgetEnrolled=N&contract=N&mode=class&c=dvfu%3Aadmission.spd&action=getStudents',
    'https://www.dvfu.ru/bitrix/services/main/ajax.php?admissionCampaignType=Магистратура&financingSource=Бюджет&studyForm=Очная&trainingDirection=01.04.02%20-%20Прикладная%20математика%20и%20информатика%20(Математические%20и%20компьютерные%20технологии)%20&sortDirection=prioritet&enrolled=N&sendorig=N&topprior=N&toppriornoorig=N&approval=N&excludeBudgetEnrolled=N&contract=N&mode=class&c=dvfu%3Aadmission.spd&action=getStudents',
    'https://www.dvfu.ru/bitrix/services/main/ajax.php?admissionCampaignType=Магистратура&financingSource=Бюджет&studyForm=Очная&trainingDirection=09.04.02%20-%20Информационные%20системы%20и%20технологии%20(Кибербезопасность%20(по%20отрасли%20или%20в%20сфере%20профессиональной%20деятельности))%20&sortDirection=prioritet&enrolled=N&sendorig=N&topprior=N&toppriornoorig=N&approval=N&excludeBudgetEnrolled=N&contract=N&mode=class&c=dvfu%3Aadmission.spd&action=getStudents',
    'https://www.dvfu.ru/bitrix/services/main/ajax.php?admissionCampaignType=Магистратура&financingSource=Бюджет&studyForm=Очная&trainingDirection=09.04.04%20-%20Программная%20инженерия%20(Разработка%20программно-информационных%20систем)%20&sortDirection=prioritet&enrolled=N&sendorig=N&topprior=N&toppriornoorig=N&approval=N&excludeBudgetEnrolled=N&contract=N&mode=class&c=dvfu%3Aadmission.spd&action=getStudents'
]
MY_NUMBER = '4351599'

def get_url_html(url : str):
    resp = requests.get(
            url = url,
            headers = {
                'User-Agent': UserAgent().random
            }
        )
    return resp

def get_user_info_all_directions():
    """
    Берёт данные о студенте на всех направлениях
    :return: JSON = {
        id:int,
        directions = [
            [
                direction:str,
                summ:int,
                priority:int,
                approval:bool
            ]
        ]
    }
    """

    students_data = {}

    for direction_name in direction_names:
        with open(f'{direction_name}.json', 'r', encoding='cp1251') as f:
            direction_data = json.load(f)
            for item in direction_data['data']:
                students_data[item] = {
                    'directions': {},
                }

    for direction_name in direction_names:
        with open(f'{direction_name}.json', 'r', encoding='cp1251') as f:
            direction_data = json.load(f)
            for item in direction_data['data']:
                direction_info = {
                    'sumscore': direction_data['data'][item]['sumscore'],
                    'selected_priority': direction_data['data'][item]['selected_priority'],
                    'approval': direction_data['data'][item]['approval']
                }
                students_data[item]['directions'][direction_data['direction']] = direction_info

    with open('JSON/students.json', 'w', encoding='cp1251') as f:
        f.write(json.dumps(students_data, indent=4, ensure_ascii=False))

def get_my_info(direction):
    with open(f'{direction}.json', 'r', encoding='cp1251') as f:
        direction_data = json.load(f)
        return direction_data['data'][MY_NUMBER]

def get_users_info_above(direction_name):
    """
    Смотрит по каждому направлению, кто выше меня и какие у него шансы на поступления на другие направления
    :return:
    """
    my_info = get_my_info(direction_name)
    data = {
        'count':0,
        'data':{},
    }
    with open('JSON/students.json', 'r', encoding='cp1251') as f:
        students_data = json.load(f)
        for student in students_data:
            if MY_NUMBER == student:
                continue
            if direction_name in students_data[student]['directions']:
                direction = students_data[student]['directions'][direction_name]
                # Если это направление, которое я сейчас смотрю
                if direction['approval'] == 'Y' and direction['sumscore'] > my_info['sumscore'] and direction['selected_priority'] <= my_info['selected_priority']:
                    data['data'][student] = direction
    data['count'] = len(data['data'])
    with open(f'exams/{direction_name}_exams.json', 'w', encoding='cp1251') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


def write_csv(direction:str,data:json):
    with open(f"{direction}.csv", "w", newline="", encoding="cp1251") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "sumscore", "selected_priority", "approval"])
        writer.writeheader()
        for item in data["data"]:
            writer.writerow({
                "id": item["ID_Student"],
                "sumscore": item["SumScore"],
                "selected_priority": item["SelectedPriority"],
                "approval": item["Approval"]
            })

def write_json(direction:str,data:json):
    new_data = {
        'direction': direction,
        'data':{}
    }
    for item in data["data"]:
        record = {
            "sumscore": item["SumScore"],
            "selected_priority": item["SelectedPriority"],
            "approval": item["Approval"]
        }
        new_data['data'][item["ID_Student"]] = record

    with open(f'{direction}.json', 'w') as f:
        f.write(json.dumps(new_data,indent=4, ensure_ascii=False))


def get_all_directions():
    directions = dict(zip(direction_names,direction_urls))

    for direction,directions_url in directions.items():
        directions_html = get_url_html(directions_url)
        direction_info_json = directions_html.json()

        # Записываем в CSV
        write_csv(direction,direction_info_json)
        # Записываем в JSON
        write_json(direction,direction_info_json)

        time.sleep(1)

# get_all_directions()
# get_user_info_all_directions()
for direction in direction_names:
    get_users_info_above(direction)


