import pandas as pd
from services.utils import format_valf_aktivasyon, list_format_sn, np_solver_lt, graph_plotter, np_solver_rpm, format_valf_aktivasyon_valf
def analyze_data(df: pd.DataFrame, columns: dict):
    """
    Verilen dataframe'den rapor sonuçlarını çıkarır.

    :param df: pandas DataFrame (Excel'den okunmuş)
    :param columns: kolon eşleştirmeleri (ör. {"rpm": "A", "su_valf": "B", ...})
    :return: dict formatında rapor çıktısı
    """
    if not columns["sicaklik"] == None:
        max_sicaklik = df[columns["sicaklik"]].max()
    else:
        max_sicaklik = None
        
    if not columns["resistans"] == None:
        resistans_sure = df[columns["resistans"]].sum() // 60
    else:
        resistans_sure = None

    tahliye_rpm = list()
    if not columns["tahliye"] == None:
        tahliye_col = df[columns["tahliye"]]
    else:
        tahliye_col = None
        
    if not columns["rpm"] == None:
        rpm_col = df[columns["rpm"]]
    else:
        rpm_col = None
        
    if rpm_col is not None and tahliye_col is not None:
        for i in range(1, len(tahliye_col)):
            if tahliye_col.iloc[i-1] == 0 and tahliye_col.iloc[i] == 1:
                if rpm_col.iloc[i] > 100:
                    tahliye_rpm.append(rpm_col.iloc[i])
        tahliye_rpm = np_solver_rpm(tahliye_rpm)
    else:
        tahliye_rpm = None
    
    if columns['twinjet'] is not None:
        twinjet_col = df[columns["twinjet"]]
        twinjet_on = (twinjet_col == 1).sum()
        twinjet_off = (twinjet_col == 0).sum() / 60
    else:
        twinjet_col = None
        twinjet_on = None
        twinjet_off = None

    report1 = {
        "max_sicaklik": f"{max_sicaklik} °C" if max_sicaklik else "N/A",
        "resistans_sure": f"{resistans_sure} dk" if resistans_sure else "N/A",
        "tahliye_rpm": f"{tahliye_rpm}" if tahliye_rpm else "N/A",
        "twinjet": {
            "on_sure": f"{twinjet_on} sn" if twinjet_on else "N/A",
            "off_sure": f"{twinjet_off:.2f} dk" if twinjet_off else "N/A",
        }
    }
########## Report 2 ##########

#    su_valf = df[columns["su_valf"]]
#    su_valf_on = (su_valf > 0).sum()
#    su_valf_off = (su_valf == 0).sum()
#    su_toplam = df[columns["su_toplam"]][su_valf == 1].last_valid_index()
#    if su_toplam:
#        su_toplam = df.at[su_toplam, columns["su_toplam"]]
#    report2 = {
#        "su_valf_on": f"{su_valf_on} sn",
#        "su_valf_off": f"{su_valf_off} sn",
#        "su_toplam": f"{su_toplam} lt" if su_toplam else "N/A"
#    }
    if columns["su_valf"] is not None:
        valf_data = df[columns["su_valf"]]
    else:
        valf_data = None
        
    if columns["su_toplam"] is not None:
        water_data = df[columns["su_toplam"]]
        total_water_consumption = df[columns["su_toplam"]].iloc[-1]
    else:
        water_data = None
        total_water_consumption = None
        
    
    if valf_data is not None and water_data is not None:
        valf_activation = list()
        water_consumption = list()
        local_valf_activation = list()
        overall_valf_activation = list()
        overall_local_valf_activation = list()
        total = 0
        total_valf_activation = len(valf_data[valf_data > 0]) / 60
        for i in range(len(valf_data)):
            if len(valf_data) == len(water_data):
                if valf_data.iloc[i] > 0 and i !=0 and i != len(valf_data)-1:
                    local_valf_activation.append(valf_data.iloc[i])
                elif (valf_data.iloc[i-1] > 0) and (valf_data.iloc[i] == 0) and (i !=0):
                    valf_activation.append(local_valf_activation)
                    water_consumption.append(water_data.iloc[i])
                    local_valf_activation = list()
                elif i == 0 and valf_data.iloc[i] > 0:
                    local_valf_activation.append(valf_data.iloc[i])
                elif i == len(valf_data) - 1 and valf_data.iloc[i] > 0:
                    local_valf_activation.append(valf_data.iloc[i])
                    valf_activation.append(local_valf_activation)
                    water_consumption.append(water_data.iloc[i])
                    local_valf_activation = list()
            else:
                print("Valf verileri ile su verileri eşleşmiyor.")
            valf_work_steps = list()
            for i in range(len(valf_activation)):
                valf_work_steps.append(len(valf_activation[i]))
            
        for val_all in valf_activation:
            for val in val_all:
                if val > 1.0:
                    total += val
            total = total / len(val_all)
            if total > 1.0:
                overall_local_valf_activation.append(total)
                overall_valf_activation.append(overall_local_valf_activation)
            total = 0
            overall_local_valf_activation = list()
        valf_activation_sequences = {}
        for i,seq in enumerate(overall_valf_activation, start=1):
            valf_activation_sequences[f'{i}. Aktivasyon'] = [round(float(x), 2) for x in seq]
    elif water_data is not None and valf_data is None:
        water_consumption = None
    else:
        valf_work_steps = None
        water_consumption = None            
        total_valf_activation = None
        valf_activation_sequences = None
    print(valf_activation)
    report2 = {
        "lokal_valf_aktivasyonları": format_valf_aktivasyon_valf(valf_activation_sequences, valf_work_steps) if valf_activation_sequences else "N/A",
        "toplam_su_tüketimi": f"{total_water_consumption} lt" if total_water_consumption else "N/A",
        "valf_çalışma_süreleri": f"{list_format_sn(valf_work_steps)}" if valf_work_steps else "N/A",
        "lokal_su_tüketimi": np_solver_lt(water_consumption) if water_consumption else "N/A",
        "toplam_valf_aktivasyonu": f"{total_valf_activation} dk" if total_valf_activation else "N/A"
    }

########## Report 3 ##########
    rpm_col = df[columns["rpm"]] if columns["rpm"] is not None else None
    max_rpm = rpm_col.max() if columns["rpm"] is not None else None
    max_rpm_sure = df[columns["rpm"]][rpm_col == max_rpm].sum() // max_rpm if columns["rpm"] is not None else None
    agitation_list = list()
    small_rpm_list = list()
    
    if columns["rpm"] is not None:
        for i in range(len(rpm_col)):
            '''motor_start = rpm_col[rpm_col > 0].first_valid_index()
            motor_end = rpm_col[motor_start:][rpm_col == 0].first_valid_index()
            motor_aralik = rpm_col[motor_start:motor_end] if motor_start and motor_end else None

            motor_devir = motor_aralik.max() if motor_aralik is not None else None
            motor_sure = len(motor_aralik) if motor_aralik is not None else None'''
            if rpm_col.iloc[i] > 0 and i != 0 and i != len(rpm_col) - 1:
                small_rpm_list.append(rpm_col.iloc[i])
            elif (rpm_col.iloc[i - 1] > 0) and (rpm_col.iloc[i] == 0) and (i != 0):
                agitation_list.append(small_rpm_list)
                small_rpm_list = list()
            elif i == 0 and rpm_col.iloc[i] > 0:
                small_rpm_list.append(rpm_col.iloc[i])
            elif i == len(rpm_col) - 1 and rpm_col.iloc[i] > 0:
                small_rpm_list.append(rpm_col.iloc[i])
                agitation_list.append(small_rpm_list)
                small_rpm_list = list()
    else:
        agitation_list = None
        small_rpm_list = None
            
    if columns['rpm'] is not None:
        motor_movement = list()
        for i in range(len(agitation_list)):
            motor_movement.append([agitation_list[i],len(agitation_list[i])])
        time_agitation = [item[1] for item in motor_movement]
    else:
        motor_movement = None
    
    if columns['rpm'] is not None:
        total = 0
        
        
        motor_agitation_sequences = {}
        for i,seq in enumerate(agitation_list, start=1):
            motor_agitation_sequences[f'{i}. Ajitasyon'] = [float(x) for x in seq]
    else:
        motor_agitation_sequences = None
        time_agitation = None
        
    #Graph params
    valf_graph = df[[columns['su_valf'], columns['su_toplam']]] if (columns['su_valf'] and columns['su_toplam']) is not None else None
    resistance_graph = df[[columns['sicaklik'], columns['resistans']]].map(lambda i : i*10 if i == 1 else i) if (columns['sicaklik'] and columns['resistans']) is not None else None
    tahliye_graph = df[columns['tahliye']] if columns['tahliye'] is not None else None
    twinjet_graph = df[columns['twinjet']] if columns['twinjet'] is not None else None
    
    graphs = {
        "Devir" : graph_plotter(rpm_col, ["Devir"],"Devir - Saniye"),
        "Valf" :  graph_plotter(valf_graph, ["Valf Debisi", "Toplam su tüketim"], "Valf debisi - Saniye\nToplam Su tüketimi - Saniye"),
        "Rezistans" : graph_plotter(resistance_graph, ["Sıcaklık", "Rezistans Çalışması"], "Sıcaklık - Saniye\nRezistans aktivitesi - Saniye"),
        "Tahliye" : graph_plotter(tahliye_graph, ["Tahile aktivitesi"], "Tahliye pompası aktivitesi - Saniye"),
        "Twinjet" : graph_plotter(twinjet_graph, ["Twinjet aktivitesi"], "Twinjet aktivitesi - Saniye")
    }
    
    report3 = {
        "max_rpm": f"{max_rpm} rpm" if max_rpm else "N/A",
        "max_rpm_sure": f"{max_rpm_sure} sn" if max_rpm_sure else "N/A",
        "motor_devir": f"{format_valf_aktivasyon(motor_agitation_sequences)}" if motor_movement else "N/A",
        "motor_sure": f"{list_format_sn(time_agitation)}" if time_agitation else "N/A"
    }

    return {
        "sicaklik_komponent": report1,
        "su_raporu": report2,
        "motor_hareketi": report3,
        "graphs" : graphs
    }
    
    