# create_data_extended.py
# سكربت لإنشاء ملف بيانات نموذجي موسع land_prices_palestine_extended.csv
import pandas as pd
import random
from datetime import datetime, timedelta

# عينات من المدن والقرى (يمكنك توسيع القائمة كما تريد)
cities = ["Ramallah","Al-Bireh","Nablus","Hebron","Bethlehem","Jenin","Tulkarm","Qalqilya","Jericho","Salfit"]
villages = ["Beitunia","Ain_Yabrud","Beit_Sahour","As_Samu","Beit_Ummar","Kafr_Qasem","Salfit_Village","Deir_Al_Ghusun","Anabta"]

terrain_choices = ["منحدر","سهل","جبل"]
earth_dirs = ["شمال","جنوب","شرق","غرب"]
street_types = ["ترابي","زفتة فرعي","زفتة رئيسي"]
area_units = ["sqm","donum","hectare","feddan"]
political_zones = ["A","B","C"]
ownership_registry = ["طابو","تسجيل جديد","مالية"]
type_of_land_choices = ["ملك","اميرية"]
shapes = ["مربعة","مستطيلة","شبه مربعة","شبه مستطيلة","موارس","شكل غير منتظم"]
soil_types = ["طمي","صخري","رملي","طيني"]

rows = []
N = 300

for i in range(N):
    if random.random() < 0.6:
        loc = random.choice(cities)
        loc_type = "city"
    else:
        loc = random.choice(villages)
        loc_type = "village"

    # مساحة بالمتر المربع أولاً ثم تحويل حسب الوحدة
    area_sqm = random.randint(100, 5000)
    area_unit = random.choice(area_units)
    if area_unit == "sqm":
        area_val = area_sqm
    elif area_unit == "donum":
        area_val = round(area_sqm / 1000, 3)   # تقريب: 1 دونم = 1000 sqm (اضبط لو تحتاج تعريف مختلف)
    elif area_unit == "hectare":
        area_val = round(area_sqm / 10000, 4)   # 1 هكتار = 10000 sqm
    elif area_unit == "feddan":
        area_val = round(area_sqm / 4200, 4)    # تقريب: 1 فدان = 4200 sqm

    frontage_exists = random.choice(["نعم","لا","لا أعلم"])
    frontage_m = random.randint(3,30) if frontage_exists == "نعم" else ""
    street_type = random.choice(street_types) if frontage_exists == "نعم" else ""
    street_width_m = random.randint(3,12) if frontage_exists == "نعم" else ""

    is_organized = random.choice([True, False])
    type_use = random.choice(["سكن أ","سكن ب","سكن ج","تجاري هامشي","مركز تجاري ب","منطقة صناعية","مكاتب"]) if is_organized else ""

    has_water = random.choice([True, False])
    has_electricity = random.choice([True, False])
    has_swer = random.choice([True, False])

    political_zone = random.choice(political_zones)
    date_of_sale = (datetime.now() - timedelta(days=random.randint(30,2000))).date().isoformat()
    price_JOD = round(random.uniform(500,100000),2)

    # المسافة من المركز
    if random.random() < 0.7:
        distance_from_center = round(random.uniform(0.1,30),3)
        distance_from_center_unit = random.choice(["m","km"])
        distance_from_center_unknown = False
    else:
        distance_from_center = ""
        distance_from_center_unit = ""
        distance_from_center_unknown = True

    # قرب الطريق الرئيسي
    if street_type == "زفتة رئيسي":
        proximity_main_road_distance = 0
        proximity_main_road_unit = "m"
        proximity_main_road_unknown = False
    else:
        if random.random() < 0.6:
            proximity_main_road_distance = round(random.uniform(0.1,50),2)
            proximity_main_road_unit = random.choice(["m","km","min"])  # min -> minutes
            proximity_main_road_unknown = False
        else:
            proximity_main_road_distance = ""
            proximity_main_road_unit = ""
            proximity_main_road_unknown = True

    proximity_services_mosque = random.choice([True, False])
    proximity_services_mosque_near_far = random.choice(["near","far"]) if proximity_services_mosque else ""

    proximity_services_school = random.choice([True, False])
    proximity_services_school_type = random.choice(["public","private"]) if proximity_services_school else ""
    proximity_services_school_near_far = random.choice(["near","far"]) if proximity_services_school else ""

    proximity_services_hospital = random.choice([True, False])
    proximity_services_hospital_type = random.choice(["clinic","hospital"]) if proximity_services_hospital else ""
    proximity_services_hospital_near_far = random.choice(["near","far"]) if proximity_services_hospital else ""

    proximity_to_sea = random.choice(["near","far","none"]) if loc in ["Gaza"] else random.choice(["far","none"])

    terrain = random.choice(terrain_choices)
    earth_direction = random.choice(earth_dirs)
    ownership_reg = random.choice(ownership_registry)
    type_of_land = random.choice(type_of_land_choices)
    shape_of_land = random.choice(shapes)
    number_of_facades = random.randint(0,4)
    soil_type = random.choice(soil_types)

    rows.append({
        'location': loc,
        'location_type': loc_type,
        'area_m2': area_val,
        'area_unit': area_unit,
        'frontage_exists': frontage_exists,
        'frontage_m': frontage_m,
        'street_type': street_type,
        'street_width_m': street_width_m,
        'is_organized': is_organized,
        'type': type_use,
        'has_water': has_water,
        'has_electricity': has_electricity,
        'has_swer': has_swer,
        'political_zone': political_zone,
        'date_of_sale': date_of_sale,
        'price_JOD': price_JOD,
        'distance_from_center': distance_from_center,
        'distance_from_center_unit': distance_from_center_unit,
        'distance_from_center_unknown': distance_from_center_unknown,
        'proximity_main_road_distance': proximity_main_road_distance,
        'proximity_main_road_unit': proximity_main_road_unit,
        'proximity_main_road_unknown': proximity_main_road_unknown,
        'proximity_services_mosque': proximity_services_mosque,
        'proximity_services_mosque_near_far': proximity_services_mosque_near_far,
        'proximity_services_school': proximity_services_school,
        'proximity_services_school_type': proximity_services_school_type,
        'proximity_services_school_near_far': proximity_services_school_near_far,
        'proximity_services_hospital': proximity_services_hospital,
        'proximity_services_hospital_type': proximity_services_hospital_type,
        'proximity_services_hospital_near_far': proximity_services_hospital_near_far,
        'proximity_to_sea': proximity_to_sea,
        'terrain': terrain,
        'earth_direction': earth_direction,
        'ownership_registry': ownership_reg,
        'type_of_land': type_of_land,
        'shape_of_land': shape_of_land,
        'number_of_facades': number_of_facades,
        'soil_type': soil_type
    })

df = pd.DataFrame(rows)
df.to_csv('land_prices_palestine_extended.csv', index=False, encoding='utf-8-sig')
print("تم إنشاء land_prices_palestine_extended.csv بنجاح ({} صف)".format(len(df)))
