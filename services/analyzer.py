import pandas as pd
from services.utils import format_valf_aktivasyon, list_format_sn, np_solver_lt, graph_plotter
def analyze_data(df: pd.DataFrame, columns: dict):
    """
    Verilen dataframe'den rapor sonuçlarını çıkarır.

    :param df: pandas DataFrame (Excel'den okunmuş)
    :param columns: kolon eşleştirmeleri (ör. {"rpm": "A", "su_valf": "B", ...})
    :return: dict formatında rapor çıktısı
    """
    max_sicaklik = df[columns["sicaklik"]].max()
    resistans_sure = df[columns["resistans"]].sum() // 60

    tahliye_rpm = list()
    tahliye_col = df[columns["tahliye"]]
    rpm_col = df[columns["rpm"]]
    for i in range(1, len(tahliye_col)):
        if tahliye_col.iloc[i-1] == 0 and tahliye_col.iloc[i] == 1:
            if rpm_col.iloc[i] > 100:
                tahliye_rpm.append(rpm_col.iloc[i])

    twinjet_col = df[columns["twinjet"]]
    twinjet_on = (twinjet_col == 1).sum()
    twinjet_off = (twinjet_col == 0).sum() / 60

    report1 = {
        "max_sicaklik": f"{max_sicaklik} °C",
        "resistans_sure": f"{resistans_sure} dk",
        "tahliye_rpm": f"{tahliye_rpm} rpm" if tahliye_rpm else "N/A",
        "twinjet": {
            "on_sure": f"{twinjet_on} sn",
            "off_sure": f"{twinjet_off:.2f} dk",
        }
    }

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

    valf_data = df[columns["su_valf"]]
    water_data = df[columns["su_toplam"]]
    total_water_consumption = df[columns["su_toplam"]].iloc[-1]
    valf_activation = list()
    water_consumption = list()
    local_valf_activation = list()
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
        
        valf_activation_sequences = {}
        for i,seq in enumerate(valf_activation, start=1):
            valf_activation_sequences[f'{i}. Aktivasyon'] = [float(x) for x in seq]
            


    report2 = {
        "lokal_valf_aktivasyonları": format_valf_aktivasyon(valf_activation_sequences) if valf_activation_sequences else "N/A",
        "toplam_su_tüketimi": f"{total_water_consumption} lt",
        "valf_çalışma_süreleri": f"{list_format_sn(valf_work_steps)}" if valf_work_steps else "N/A",
        "lokal_su_tüketimi": np_solver_lt(water_consumption) if water_consumption else "N/A",
        "toplam_valf_aktivasyonu": f"{total_valf_activation} dk" if total_valf_activation else "N/A"
    }

########## Report 3 ##########
    rpm_col = df[columns["rpm"]]
    max_rpm = rpm_col.max()
    max_rpm_sure = df[columns["rpm"]][rpm_col == max_rpm].sum() // max_rpm
    agitation_list = list()
    small_rpm_list = list()
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
            
    motor_movement = list()
    for i in range(len(agitation_list)):
        motor_movement.append([agitation_list[i],len(agitation_list[i])])
    time_agitation = [item[1] for item in motor_movement]
    
    motor_agitation_sequences = {}
    for i,seq in enumerate(agitation_list, start=1):
        motor_agitation_sequences[f'{i}. Ajitasyon'] = [float(x) for x in seq]
        
    #Graph
    '''
    graphs = {
        "Devir" : graph_plotter(rpm_col, "Devir - Dakika"),
        "Valf" :  graph_plotter(pd.concat([valf_data, water_data]), "Valf debisi - Dakika\nToplam Su tüketimi - Dakika"),
        "Rezistans" : graph_plotter(pd.concat([df['sicaklik'], df['rezistans']*10]), "Sıcaklık - Dakika\nRezistans aktivitesi - Dakika"),
        "Tahliye" : graph_plotter(df['tahliye'], "Tahliye pompası aktivitesi - Dakika"),
        "Twinjet" : graph_plotter(df['twinjet'], "Twinjet aktivitesi - Dakika")
    }
    '''
    report3 = {
        "max_rpm": f"{max_rpm} rpm",
        "max_rpm_sure": f"{max_rpm_sure} sn",
        "motor_devir": f"{format_valf_aktivasyon(motor_agitation_sequences)}" if motor_movement else "N/A",
        "motor_sure": f"{list_format_sn(time_agitation)}" if time_agitation else "N/A"
    }

    return {
        "sicaklik_komponent": report1,
        "su_raporu": report2,
        "motor_hareketi": report3,
    }
    
    