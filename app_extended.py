# app_extended_fixed_enhanced.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import joblib

# ----------------- إعداد الصفحة -----------------
st.set_page_config(page_title="تقييم أسعار الأراضي - محدث ومحسن", layout="wide", initial_sidebar_state="collapsed")
st.title("🏡 تطبيق تقدير سعر الأرض — نسخة محسّنة 📈")

# ----------------- قوائم أمثلة -----------------
cities = ["Ramallah","Al-Bireh","Nablus","Hebron","Bethlehem","Jenin","Tulkarm","Qalqilya","Jericho","Salfit"]
villages = ["Beitunia","Ain_Yabrud","Beit_Sahour","As_Samu","Beit_Ummar","Kafr_Qasem","Salfit_Village","Deir_Al_Ghusun","Anabta"]

# ----------------- حقول ثابتة للاختيار -----------------
area_units = {"متر مربع (sqm)":"sqm","دونم":"donum","هكتار":"hectare","فدان":"feddan"}
street_types = ["ترابي","زفتة فرعي","زفتة رئيسي"]
terrain_choices = ["منحدر","سهل","جبل"]
earth_dirs = ["شمال","جنوب","شرق","غرب"]
ownership_registry_list = ["طابو","تسجيل جديد","مالية"]
type_of_land_choices = ["ملك","اميرية"]
shapes = ["مربعة","مستطيلة","شبه مربعة","شبه مستطيلة","موارس","شكل غير منتظم"]
soil_types = ["طمي","صخري","رملي","طيني"]
political_zones = ["A","B","C"]

# دالة تحويل المساحة
def to_sqm(val, unit):
    if unit == "sqm": return val
    if unit == "donum": return val*1000
    if unit == "hectare": return val*10000
    if unit == "feddan": return val*4200
    return val

# ----------------- 1. نوع ومكان الأرض -----------------
with st.expander("📍 **1. الموقع ونطاق الأرض**", expanded=True):
    location_scope = st.radio("هل الأرض داخل:", ("داخل مدينة","داخل قرية","خارج حدود المدينة/القرية"), key="loc_scope", horizontal=True)
    search_term = st.text_input("ابحث باسم المدينة/القرية (اتركه فارغاً لعرض الكل)", key="search_term", help="يمكنك البدء بكتابة جزء من اسم الموقع لتصفيته.")

    if location_scope == "داخل مدينة":
        options = cities
    elif location_scope == "داخل قرية":
        options = villages
    else:
        options = []

    filtered = [o for o in options if search_term.lower() in o.lower()] if search_term else options
    
    if location_scope != "خارج حدود المدينة/القرية":
        location = st.selectbox("اختر الموقع", ["-- اختر --"] + filtered, index=0, key="location")
        if location == "-- اختر --":
            location = ""
    else:
        location = ""
        st.info("🗺️ **الأرض خارج حدود المدينة/القرية** — لا يمكن اختيار اسم موقع محدد من القائمة.")

st.markdown("---")

# ----------------- 2. المساحة والوحدات -----------------
with st.container(border=True):
    st.subheader("📏 **2. قياسات ومساحة الأرض**")
    col1, col2 = st.columns([2,1])
    with col1:
        area_value = st.number_input("أدخل قيمة المساحة", min_value=0.0, value=0.0, step=1.0, format="%.3f", key="area_value")
    with col2:
        area_unit_label = st.selectbox("وحدة المساحة", list(area_units.keys()), index=0, key="area_unit_label")
        area_unit = area_units[area_unit_label]

    area_m2_converted = to_sqm(area_value, area_unit)
    st.markdown(f"**المساحة المحولة بالمتر المربع (sqm):** **`{area_m2_converted:,.2f}`** متر مربع.")

st.markdown("---")

# ----------------- 3. الواجهة والشوارع -----------------
with st.expander("🛣️ **3. واجهة الأرض والشوارع**"):
    frontage = st.radio("هل يوجد واجهة على الشارع؟", ("-- اختر --","نعم","لا","لا أعلم"), index=0, key="frontage", horizontal=True)
    frontage_m = street_type = street_width_m = ""
    
    if frontage == "نعم":
        col1, col2, col3 = st.columns(3)
        with col1:
            frontage_m = st.number_input("طول الواجهة بالمتر", min_value=0.0, step=0.5, value=0.0, key="frontage_m")
        with col2:
            street_type = st.selectbox("نوع الشارع", street_types, key="street_type")
        with col3:
            street_width_m = st.number_input("عرض الشارع (متر)", min_value=0.0, step=0.5, value=0.0, key="street_width_m")
    elif frontage == "لا":
        st.warning("⚠️ لا يوجد واجهة على شارع — قد يؤثر على التقييم.")

st.markdown("---")

# ----------------- 4. المخطط ونوع الاستعمال -----------------
with st.container(border=True):
    st.subheader("🏗️ **4. المخطط ونوع الاستعمال**")
    is_organized = st.checkbox("**هل الأرض ضمن المخطط الهيكلي للمنطقة؟**", key="is_organized")
    type_use = ""
    if is_organized:
        type_use = st.selectbox("نوع الاستعمال المخطط", ["-- اختر --","سكن أ","سكن ب","سكن ج","تجاري هامشي","مركز تجاري ب","منطقة صناعية","مكاتب"], index=0, key="type_use")
        if type_use == "-- اختر --":
            type_use = ""
        if not type_use:
            st.error("❌ **يرجى اختيار نوع الاستعمال لتطبيق ضمن المخطط.**")
    else:
        st.info("الأرض غير منظمة — لا ينطبق نوع الاستعمال المخطط.")

st.markdown("---")

# ----------------- 5. الخدمات الأساسية -----------------
with st.expander("💧💡🚽 **5. توفر الخدمات الأساسية**"):
    col1, col2, col3 = st.columns(3)
    with col1:
        has_water = st.checkbox("شبكة مياه متوفرة؟", key="has_water")
    with col2:
        has_electricity = st.checkbox("شبكة كهرباء متوفرة؟", key="has_electricity")
    with col3:
        has_swer = st.checkbox("شبكة صرف صحي متوفرة؟", key="has_swer")

st.markdown("---")

# ----------------- 6. الموقع السياسي والمسافات -----------------
with st.expander("⚖️ **6. المنطقة السياسية والمسافات**"):
    col1, col2 = st.columns(2)
    with col1:
        political_zone = st.selectbox("المنطقة السياسية", ["-- اختر --"]+political_zones, index=0, key="political_zone", help="اختر المنطقة السياسية (A، B، أو C).")
        if political_zone == "-- اختر --":
            political_zone = ""
    with col2:
        distance_unknown = st.checkbox("لا أعرف المسافة من مركز المدينة/القرية", key="distance_unknown")
        dist_val = dist_unit = ""
        if not distance_unknown:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                dist_val = st.number_input("المسافة من المركز", min_value=0.0, value=0.0, step=0.1, key="dist_val")
            with col_d2:
                dist_unit = st.selectbox("وحدة المسافة", ["m","km"], key="dist_unit")
        else:
            st.info("سيتم استخدام قيمة افتراضية للنموذج لعدم معرفة المسافة.")

st.markdown("---")

# ----------------- 7. قرب الطريق الرئيسي -----------------
with st.expander("🚗 **7. القرب من الطريق الرئيسي**"):
    
    proximity_main_road_distance = proximity_main_road_unit = proximity_main_road_unknown = ""

    if frontage == "نعم" and street_type == "زفتة رئيسي":
        st.success("✅ **الأرض على شارع رئيسي** — لا حاجة لإدخال قرب الطريق.")
        proximity_main_road_distance = 0
        proximity_main_road_unit = "m"
        proximity_main_road_unknown = False
    else:
        prox_unknown = st.radio("هل تعرف مسافة الطريق الرئيسي القريب؟", ("-- اختر --","أعرف المسافة","لا أعرف","بعيدة جداً"), index=0, key="prox_unknown", horizontal=True)
        
        if prox_unknown == "أعرف المسافة":
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                proximity_main_road_distance = st.number_input("أدخل المسافة", min_value=0.0, value=0.0, step=0.1, key="prox_main_dist")
            with col_p2:
                proximity_main_road_unit = st.selectbox("وحدة المسافة/الزمن", ["m","km","min"], key="prox_main_unit")
            proximity_main_road_unknown = False
        elif prox_unknown == "لا أعرف":
            proximity_main_road_distance = ""
            proximity_main_road_unit = ""
            proximity_main_road_unknown = True
            st.info("سيتم تقدير قرب الطريق الرئيسي بواسطة النموذج (إذا كان النموذج يدعم ذلك).")
        else: # بعيدة جداً
            proximity_main_road_distance = 5000 # قيمة افتراضية كبيرة (5 كم)
            proximity_main_road_unit = "m"
            proximity_main_road_unknown = False
            st.info("تم اعتبار المسافة بعيدة جداً.")

st.markdown("---")

# ----------------- 8. قرب الخدمات -----------------
with st.expander("🏥🕌 **8. قرب الخدمات (مسجد، مدارس، مستشفى)**"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        prox_mosque = st.selectbox("هل يوجد مسجد قريب؟", ("-- اختر --","نعم","لا"), index=0, key="prox_mosque")
        prox_mosque_nearfar = ""
        if prox_mosque == "نعم":
            prox_mosque_nearfar = st.radio("القرب:", ("near","far"), key="prox_mosque_nearfar", horizontal=True)

    with col2:
        prox_school = st.selectbox("هل توجد مدرسة؟", ("-- اختر --","نعم","لا"), index=0, key="prox_school")
        prox_school_type = prox_school_nearfar = ""
        if prox_school == "نعم":
            prox_school_type = st.radio("نوع المدرسة:", ("public","private"), key="prox_school_type", horizontal=True)
            prox_school_nearfar = st.radio("القرب:", ("near","far"), key="prox_school_nearfar", horizontal=True)

    with col3:
        prox_hospital = st.selectbox("هل يوجد مستشفى/عيادة؟", ("-- اختر --","نعم","لا"), index=0, key="prox_hospital")
        prox_hospital_type = prox_hospital_nearfar = ""
        if prox_hospital == "نعم":
            prox_hospital_type = st.radio("نوع المرفق:", ("clinic","hospital"), key="prox_hospital_type", horizontal=True)
            prox_hospital_nearfar = st.radio("القرب:", ("near","far"), key="prox_hospital_nearfar", horizontal=True)

st.markdown("---")

# ----------------- 9. بقية الحقول -----------------
with st.expander("📜 **9. خصائص إضافية للأرض (الطبيعة والملكية)**"):
    st.subheader("الخصائص الطبيعية والشكل")
    col1, col2, col3 = st.columns(3)
    with col1:
        terrain = st.selectbox("التضاريس", ["-- اختر --"]+terrain_choices, index=0, key="terrain")
        if terrain == "-- اختر --": terrain = ""
        earth_direction = st.selectbox("اتجاه الأرض", ["-- اختر --"]+earth_dirs, index=0, key="earth_dir")
        if earth_direction == "-- اختر --": earth_direction = ""
        soil_type = st.selectbox("نوع التربة", ["-- اختر --"]+soil_types, index=0, key="soil_type")
        if soil_type == "-- اختر --": soil_type = ""
    
    with col2:
        st.subheader("الملكية والتسجيل")
        ownership_registry = st.selectbox("نظام التسجيل", ["-- اختر --"]+ownership_registry_list, index=0, key="ownership_reg")
        if ownership_registry == "-- اختر --": ownership_registry = ""
        type_of_land = st.selectbox("نوع الملكية", ["-- اختر --"]+type_of_land_choices, index=0, key="type_land")
        if type_of_land == "-- اختر --": type_of_land = ""

    with col3:
        st.subheader("الشكل والواجهات")
        shape_of_land = st.selectbox("شكل الأرض", ["-- اختر --"]+shapes, index=0, key="shape_land")
        if shape_of_land == "-- اختر --": shape_of_land = ""
        number_of_facades = st.number_input("عدد واجهات الشارع", min_value=0, max_value=10, value=0, step=1, key="num_facades")

st.markdown("---")

# ----------------- 10. حفظ الإدخال وتقدير السعر -----------------
st.header("✨ **10. تقدير السعر وحفظ البيانات**")

logs_file = "logs.csv"
model_path = "land_price_model_extended.pkl"

if st.button("🚀 **تقدير السعر / حفظ الإدخال**", type="primary", use_container_width=True):
    
    # التحقق من المدخلات
    errors = []
    if location_scope != "خارج حدود المدينة/القرية" and not location:
        errors.append("يجب اختيار اسم المدينة/القرية أو الخروج من النطاق المحدد.")
    if area_value <= 0:
        errors.append("الرجاء إدخال مساحة صحيحة أكبر من صفر.")
    if is_organized and not type_use:
        errors.append("اختر نوع الاستعمال لأن الأرض ضمن المخطط الهيكلي.")
    if not ownership_registry:
        errors.append("يجب اختيار نظام التسجيل.")

    if errors:
        st.error("❌ **لم يتم التقدير! يرجى تصحيح الأخطاء التالية:**")
        for e in errors:
            st.markdown(f"- {e}")
    else:
        # بناء السجل (كما كان)
        record = {
            'timestamp': datetime.now().isoformat(),
            'location': location,
            'location_scope': location_scope,
            'area_value': area_value,
            'area_unit': area_unit,
            'area_m2_converted': area_m2_converted,
            'frontage': frontage,
            'frontage_m': frontage_m,
            'street_type': street_type,
            'street_width_m': street_width_m,
            'is_organized': is_organized,
            'type': type_use,
            'has_water': has_water,
            'has_electricity': has_electricity,
            'has_swer': has_swer,
            'political_zone': political_zone,
            'distance_from_center': dist_val,
            'distance_from_center_unit': dist_unit,
            'distance_from_center_unknown': distance_unknown,
            'proximity_main_road_distance': proximity_main_road_distance,
            'proximity_main_road_unit': proximity_main_road_unit,
            'proximity_main_road_unknown': proximity_main_road_unknown,
            'proximity_services_mosque': prox_mosque == "نعم",
            'proximity_services_mosque_near_far': prox_mosque_nearfar,
            'proximity_services_school': prox_school == "نعم",
            'proximity_services_school_type': prox_school_type,
            'proximity_services_school_near_far': prox_school_nearfar,
            'proximity_services_hospital': prox_hospital == "نعم",
            'proximity_services_hospital_type': prox_hospital_type,
            'proximity_services_hospital_near_far': prox_hospital_nearfar,
            'terrain': terrain,
            'earth_direction': earth_direction,
            'ownership_registry': ownership_registry,
            'type_of_land': type_of_land,
            'shape_of_land': shape_of_land,
            'number_of_facades': int(number_of_facades),
            'soil_type': soil_type
        }

        # تقدير السعر باستخدام النموذج
        price_estimated = None
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                df_input = pd.DataFrame([record])
                
                # تهيئة البيانات للنموذج
                df_input['area_m2'] = df_input['area_m2_converted']
                df_input['location_type'] = df_input['location_scope'].map({
                    "داخل مدينة": "city",
                    "داخل قرية": "village",
                    "خارج حدود المدينة/القرية": "outside"
                })
                # يجب تهيئة الأعمدة الفئوية الأخرى للنموذج هنا إذا لزم الأمر
                # (لأغراض العرض، نفترض أن النموذج يتعامل مع البيانات المُدخلة)

                pred = model.predict(df_input)
                price_estimated = pred[0]
                record['price_estimated_JOD'] = price_estimated

                st.subheader("💵 **السعر المقدر**")
                st.balloons() # إضافة احتفال بالتقدير
                st.success(f"**القيمة التقديرية (JOD):** **{price_estimated:,.2f}** دينار أردني. 🎉", icon="💰")

                # زر تنزيل التقرير (شكلي)
                st.button("📄 **تنزيل/طباعة التقرير** (غير مفعل حالياً)", disabled=True)

            except Exception as e:
                st.warning(f"⚠️ **خطأ عند تحميل أو تشغيل النموذج:** لم نتمكن من التقدير. ({str(e)})")
        else:
            st.info("ℹ️ **ملف النموذج مفقود:** لا يمكن تقدير السعر حالياً (ملف `land_price_model_extended.pkl`).")

        # حفظ البيانات في logs.csv
        try:
            if not os.path.exists(logs_file):
                pd.DataFrame([record]).to_csv(logs_file, index=False, encoding='utf-8-sig')
                st.success(f"💾 تم إنشاء الملف وحفظ بيانات الإدخال في **{logs_file}**.", icon="✅")
            else:
                pd.DataFrame([record]).to_csv(logs_file, index=False, header=False, mode='a', encoding='utf-8-sig')
                st.success(f"💾 تم إضافة بيانات الإدخال إلى **{logs_file}**.", icon="✅")
        except Exception as e:
            st.error(f"❌ **خطأ في حفظ البيانات:** لم نتمكن من الحفظ في ملف logs.csv. ({str(e)})")


st.markdown("---")
st.caption("© **ملاحظة:** هذا التطبيق يحفظ كل إدخال في ملف `logs.csv` لاستخدامه في تدريب نموذج لاحقاً.")
st.caption("تم تطوير التطبيق لأغراض تقييم أسعار الأراضي في فلسطين.")