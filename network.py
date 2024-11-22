import os
import csv
from flask import Flask, render_template, request

# إعداد تطبيق Flask
app = Flask(__name__)

# دالة لقراءة البيانات من ملف CSV
def read_data_from_csv():
    if not os.path.exists('network_data.csv'):
        return []
    with open('network_data.csv', mode='r') as file:
        reader = csv.reader(file)
        return list(reader)

# صفحة الفلترة
@app.route('/filter_data', methods=['GET', 'POST'])
def filter_data():
    # قراءة البيانات من ملف CSV
    data = read_data_from_csv()

    # إذا كان هناك طلب فلترة
    if request.method == 'POST':
        filter_value = request.form.get('filter_value')  # قيمة الفلتر المدخلة
        if filter_value:
            # تصفية البيانات حسب القيمة المدخلة
            filtered_data = [row for row in data if filter_value.lower() in str(row).lower()]
            return render_template('filter_data.html', data=filtered_data)
        else:
            return render_template('filter_data.html', data=data)

    # في حال لم يكن هناك طلب فلترة، عرض البيانات الكاملة
    return render_template('filter_data.html', data=data)

# صفحة العرض الرئيسية
@app.route('/')
def index():
    data = read_data_from_csv()
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
