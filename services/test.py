import pandas as pd
from analyzer import analyze_data

# test_analyzer.py

'''data = {
    "rpm": [0, 120, 170, 180, 0, 160, 130],
    "su_valf": [0, 7.01, 6.82, 0, 5.83, 6.91, 5.23],
    "su_toplam": [0, 11.83, 15, 15, 15, 20, 20],
    "sicaklik": [20, 30, 40, 50, 60, 55, 45],
    "resistans": [60, 60, 60, 60, 60, 60, 60],
    "tahliye": [0, 0, 1, 1, 0, 1, 0],
    "twinjet": [1, 0, 1, 0, 1, 0, 1],
    "zaman": [0, 1, 2, 3, 4, 5, 6]
}
df = pd.DataFrame(data)
columns = {
    "rpm": "rpm",
    "su_valf": "su_valf",
    "su_toplam": "su_toplam",
    "sicaklik": "sicaklik",
    "resistans": "resistans",
    "tahliye": "tahliye",
    "twinjet": "twinjet",
    "zaman": "zaman"
}
result = analyze_data(df, columns)
print(result)'''
'''assert "sicaklik_komponent" in result
assert "su_raporu" in result
assert "motor_hareketi" in result

# Check some expected values
assert result["sicaklik_komponent"]["max_sicaklik"] == "60 °C"
assert result["sicaklik_komponent"]["resistans_sure"] == "7 dk"
assert "rpm" in result["sicaklik_komponent"]["tahliye_rpm"] or result["sicaklik_komponent"]["tahliye_rpm"] == "N/A"
assert result["sicaklik_komponent"]["twinjet"]["on_sure"].endswith("sn")
assert result["sicaklik_komponent"]["twinjet"]["off_sure"].endswith("sn")

assert result["su_raporu"]["su_valf_on"].endswith("sn")
assert result["su_raporu"]["su_valf_off"].endswith("sn")
assert "lt" in result["su_raporu"]["su_toplam"] or result["su_raporu"]["su_toplam"] == "N/A"

assert result["motor_hareketi"]["max_rpm"] == "150 rpm"
assert result["motor_hareketi"]["max_rpm_sure"].endswith("sn")
assert "rpm" in result["motor_hareketi"]["motor_devir"] or result["motor_hareketi"]["motor_devir"] == "N/A"
assert "sn" in result["motor_hareketi"]["motor_sure"] or result["motor_hareketi"]["motor_sure"] == "N/A" '''

import pandas as pd
columns = [chr(i) for i in range(ord("A"), ord("Z")+1)]
columns += [f"A{chr(i)}" for i in range(ord("A"), ord("Q")+1)]
df = pd.read_csv('C:\\Users\\gorkemk\\Desktop\\Test Qualification Improvment\\SAP_Automation\\Panel Test Data Analyzer\\Pano data.csv',sep=";", engine='python', on_bad_lines='skip', header=None)
df.columns = columns[:len(df.columns)]

print(df.tail())

