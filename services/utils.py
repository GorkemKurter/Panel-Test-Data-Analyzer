import plotly.express as px
import pandas as pd
def format_valf_aktivasyon_valf(data: dict, extra_list: list) -> str:
    formatted_lines = []
    for i, (key, values) in enumerate(data.items()):
        values_str = ", ".join(map(str, values))
        extra = f", {extra_list[i]} saniye boyunca" if i < len(extra_list) else ""
        formatted_lines.append(
            f"<strong style='text-decoration: underline; color:#ec3a40ff'>{key}:<br></strong>{values_str}{extra}"
        )
    return "<br><br>".join(formatted_lines)

def list_format_sn(data: list) -> str:
    return " sn , ".join(map(str, data)) + " sn"

def list_format_lt(data: list) -> str:
    return " lt , ".join(map(str, data)) + " lt"

def np_solver_lt(data: list) -> str:
    return " lt , ".join(map(str, [float(x) for x in data])) + " lt"

def np_solver_rpm(data: list) -> str:
    return " rpm , ".join(map(str, [float(x) for x in data])) + " rpm"

def graph_plotter(df, param, title):

    if isinstance(df, pd.DataFrame) or isinstance(df, pd.Series):
        if df.all() is not None:
            for i in range(len(param)):
                if isinstance(df, pd.DataFrame):
                    df = df.rename(columns={df.columns[i]: param[i]})
                else:
                    df = df.rename(param[i])
            fig = px.line(
                data_frame = df,
                title = title,
                labels = {"value" : "Değer", "index" : "Saniye"},
                template="plotly_dark"
            )
            
            graph_html = fig.to_html(full_html=True)
            
            return graph_html
        else:
            graph_html = "Veri bulunamadı!"
            return graph_html
    else:
        graph_html = "Veri bulunamadı!"
        return graph_html

#import plotly.io as pio
#pio.write_html(fig, file=html_file, auto_open=True)

def format_valf_aktivasyon(data: dict) -> str:
    formatted_lines = []
    for key, values in data.items():
        values_str = ", ".join(map(str, values))
        formatted_lines.append(f"<strong style='text-decoration: underline; color:#ec3a40ff'>{key}:<br></strong>{values_str}")
    return "<br><br>".join(formatted_lines)