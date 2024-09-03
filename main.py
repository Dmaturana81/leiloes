from email.policy import default
import streamlit as st

from model import (
    CashFlow,
    Imovel,
    Leilao,
    Pos_imissao,
    Custo_arrematacao,
    Posposse,
    Impostos,
)
from mortgage import Mortgage_price


def calculate(**kwargs):
    cashflow = CashFlow(**kwargs)
    cashflow_f = CashFlow(financiamento=True, **kwargs)
    container1 = st.container()
    container1.title("Resultados")
    a, b = container1.columns(2)
    a.header("A vista")
    data = cashflow.do_all()
    for k, v in data.items():
        if isinstance(v, float):
            a.write(f"{k}: ${v:,.2f}".format(k=k, v=round(v, 2))) if k.lower() not in [
                "roi"
            ] else a.write(f"{k}: {v:,.2f}%".format(k=k, v=round(v, 2)))
    # a.write(f"Total Despesas: {cashflow.calculo_total_despesas()}")
    # a.write(f"Receita Liquida: {cashflow.calculo_receta_liquida()}")
    # a.write(f"Lucro Bruto: {cashflow.calculo_lucro_bruto()}")
    # a.write(f"Lucro Liquido: {cashflow.calculo_lucro_liquido()}")
    # a.write(f"ROI: {cashflow.calculo_roi()}")
    # a.write(f"Ganho Capital: {cashflow.calculo_ganho_capital()}")
    # a.write(
    #     f"Comissão Leiloeiro: {cashflow.arrematacao.valor_comissao_leiloero(cashflow.leilao.valor_arremate)}"
    # )
    # a.write(cashflow.arrematacao.valor_itbi(cashflow.leilao.valor_arremate))
    # a.write(cashflow.arrematacao.valor_total_registro(cashflow.leilao.valor_arremate))

    b.header("Com financiamento")
    data_f = cashflow_f.do_all()
    for k, v in data_f.items():
        b.write(f"{k}: ${v:,.2f}".format(k=k, v=round(v, 2))) if k.lower() not in [
            "roi"
        ] else b.write(f"{k}: {v:,.2f}%".format(k=k, v=round(v, 2)))  # ${:,.2f}
        # b.write(cashflow_f.calculo_total_despesas())
    # b.write(cashflow_f.calculo_receta_liquida())
    # b.write(cashflow_f.calculo_lucro_bruto())
    # b.write(cashflow_f.calculo_lucro_liquido())
    # b.write(cashflow_f.calculo_roi())
    # b.write(cashflow_f.leilao.calculo_total_arremate())
    # b.write(cashflow_f.calculo_ganho_capital())
    # b.write(
    #     cashflow_f.arrematacao.valor_comissao_leiloero(cashflow.leilao.valor_arremate)
    # )
    # b.write(cashflow_f.arrematacao.valor_itbi(cashflow.leilao.valor_arremate))
    # b.write(cashflow_f.arrematacao.valor_total_registro(cashflow.leilao.valor_arremate))
    container2 = st.container()
    container2.title("Plots")


# Streamlit application code
if __name__ == "__main__":
    st.title("Real Estate Sales App")
    sidebar = st.sidebar
    # Render sidebar with form inputs using a for loop to create each input element
    sidebar.header("Detalhes Leilao")
    expander = sidebar.expander("Detalhes Leilao", expanded=True)
    leilao_dict = {}
    imovel_dict = {}
    # write the form fields for the class Imovel
    for k, v in Leilao.schema()["properties"].items():
        if k in ["id_", "url"]:
            continue
            leilao_dict[k] = expander.text_input(k, key=k)
        elif k.startswith("pc") or k in ["valor_arremate"]:
            continue
        else:
            leilao_dict[k] = expander.number_input(k, key=k, value=v["default"])

    entrada = expander.number_input("Entrada %", key="entrada", value=5)

    sidebar.header("Detalhes Imovel")
    expander = sidebar.expander("Detalhes Imovel", expanded=True)
    # write the form fields for the class Imovel
    for k, v in Imovel.schema()["properties"].items():
        imovel_dict[k] = expander.number_input(k, key=k, value=v["default"])

    sidebar.header("Custos")
    expander = sidebar.expander("Post imissão", expanded=False)
    custos_dict = {}
    # write the form fields for the class Imovel
    for k, v in Pos_imissao.schema()["properties"].items():
        custos_dict[k] = expander.number_input(k, key=k, value=v["default"])

    expander = sidebar.expander("Arrematacao", expanded=False)
    arrematacao_dict = {}
    # write the form fields for the class Imovel
    for k, v in Custo_arrematacao.schema()["properties"].items():
        if k.startswith("pc"):
            continue
        arrematacao_dict[k] = expander.number_input(
            k, key=k, value=v["default"] if "default" in v else 0
        )

    # expander = sidebar.expander("Mortgage", expanded=False)
    # mortgage_dict = {}
    # # write the form fields for the class Imovel
    # for k, v in Mortgage_price.schema()["properties"].items():
    #     mortgage_dict[k] = expander.number_input(k, key=k, value=v["default"])

    expander = sidebar.expander("Post Posse", expanded=False)
    posposse_dict = {}
    # write the form fields for the class Imovel
    for k, v in Posposse.schema()["properties"].items():
        if k in ["imovel"]:
            continue
        posposse_dict[k] = expander.number_input(k, key=k, value=v["default"])

    expander = sidebar.expander("Imposto", expanded=False)
    imposto_dict = {}
    # write the form fields for the class Imovel
    for k, v in Impostos.schema()["properties"].items():
        imposto_dict[k] = expander.number_input(k, key=k, value=v["default"])

    sidebar.button(
        "Calculate",
        key="calculate",
        on_click=calculate(
            imovel=imovel_dict,
            leilao=leilao_dict,
            extras=custos_dict,
            arrematacao=arrematacao_dict,
            posposse=posposse_dict,
            impostos=imposto_dict,
            pc_entrada=(entrada / 100),
        ),
    )
    # Example of processing the data (This would need actual business logic based on your requirements):
