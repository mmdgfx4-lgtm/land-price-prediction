# train_model_extended.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# تحميل البيانات
csv_file = "land_prices_palestine_extended.csv"
if not os.path.exists(csv_file):
    print("ملف البيانات '{}' غير موجود. تأكد من تشغيل create_data_extended.py أولاً.".format(csv_file))
    exit()

df = pd.read_csv(csv_file, encoding='utf-8-sig')

# ملاحظات المعالجة:
# - نتأكد من تحويل المساحات للوحدة المترية (area_m2 مكتوب مُسبقاً في السكربت المنشئ)
# - نملأ القيم الفارغة بطرق مبسطة (يمكن تحسينها لاحقاً)
# - نختار بعض الميزات المفترضة للموديل

# تنظيف / ملء القيم البسيطة
df['area_m2'] = pd.to_numeric(df['area_m2'], errors='coerce')
df['area_m2'] = df['area_m2'].fillna(df['area_m2'].median())

# لبعض الأعمدة البوليانية / الفئوية:
bool_cols = ['has_water','has_electricity','has_swer','is_organized','proximity_services_mosque','proximity_services_school','proximity_services_hospital']
for c in bool_cols:
    if c in df.columns:
        df[c] = df[c].fillna(False)

# لعوامد المسافة: تحويل القيم النصية الفارغة إلى NaN
num_cols = ['frontage_m','street_width_m','distance_from_center','proximity_main_road_distance']
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)

# الهدف: price_JOD
df['price_JOD'] = pd.to_numeric(df['price_JOD'], errors='coerce').fillna(df['price_JOD'].median())

# دعنا نحدد الميزات التي سنستخدمها (يمكن تعديلها لاحقاً)
features = [
    'area_m2','frontage_m','street_width_m','has_water','has_electricity','has_swer',
    'is_organized','distance_from_center','proximity_main_road_distance',
    'terrain','earth_direction','ownership_registry','type_of_land','shape_of_land','soil_type','location_type','location','street_type'
]
# تأكد من وجود الميزات في df، وإلا أحذفها من القائمة
features = [f for f in features if f in df.columns]

X = df[features]
y = df['price_JOD']

# نوعي بعض الأعمدة العددية و الفئوية
numeric_features = ['area_m2','frontage_m','street_width_m','distance_from_center','proximity_main_road_distance']
numeric_features = [f for f in numeric_features if f in X.columns]
categorical_features = [c for c in X.columns if c not in numeric_features]

# تعويض القيم الفارغة في الفئات
X[categorical_features] = X[categorical_features].fillna("unknown")

# بناء المحول
numeric_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1))
])

# تقسيم وتدريب
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("بدء التدريب...")
model.fit(X_train, y_train)
print("تم التدريب.")

# تقييم سريع
score = model.score(X_test, y_test)
print(f"R^2 on test set: {score:.3f}")

# حفظ الموديل
joblib.dump(model, "land_price_model_extended.pkl")
print("تم حفظ النموذج في land_price_model_extended.pkl")
