from pyexpat import model
from pydantic import BaseModel, Field, model_validator, field_validator

from mortgage import Mortgage_price


class Imovel(BaseModel):
    """Class to represent a Imovel"""

    valor_venda: float = Field(default=200000, alias="Valor Venta", ge=0)  # Fixo,

    valor_iptu: float = Field(default=50.0, alias="IPTU", ge=0)
    valor_condominio: float = Field(default=300.0, alias="Condominio", ge=0)
    valor_corretor: float = Field(default=5, alias="Comision", ge=0)  # Percentage
    valor_aluguel: float = Field(default=0.0, alias="Valor Aluguel")

    @field_validator("valor_corretor")
    def val_to_per(cls, value):
        cls.pc_corretor = value / 100

    def custos_mensais(self, parcela: float = 0):
        """Calcular custos mensais = IPTU + Condominio. Caso de ter Aluguel = Aluguel - (IPTU + Condominio)"""
        return (
            self.valor_iptu + self.valor_condominio + parcela - self.valor_aluguel
            # if self.valor_aluguel is None
            # else self.valor_aluguel
            # - (self.valor_iptu + self.valor_condominio + parcela)
        )

    def calculo_receita_liq(self, saldo_devedor: float | None):
        """Calcular receita liquida = Valor Venta * (1 - Comision) - saldo devedor"""
        return self.valor_venda * (1 - self.pc_corretor) - saldo_devedor


class Leilao(BaseModel):
    """Class to represent a Leilao"""

    id_: str = ""
    url: str = ""
    valor_inicial: float = Field(default=100000, alias="Valor Inicial", ge=0)
    lance_minimo: float = Field(default=5000, alias="Lance minimo", ge=0)
    valor_arremate: float
    n_lance: int = Field(default=1, alias="Lance", ge=0)
    # financiamento: int = Field(default=95, alias="Financiado")
    # pc_financiado: float

    @model_validator(mode="before")
    @classmethod
    def validate_valor_arremate(cls, values):
        values["valor_arremate"] = values["Valor Inicial"] + (
            values["Lance minimo"] * values["Lance"]
        )
        # values["pc_financiado"] = values["Financiado"] / 100
        return values

    def actualizar_valor(self, n_lances: int):
        """Actualizar valor lance arremate"""
        self.valor_arremate = self.valor_inicial + n_lances * self.lance_minimo

    def actualizar_lance(self):
        """Actualizar numero de lances"""
        self.n_lance += 1

    def calculo_total_arremate(self):
        """Calcular total = valor_arremate * n_lance"""
        self.valor_arremate = (
            self.valor_inicial + (self.lance_minimo * self.n_lance)
            # if not self.financiamento
            # else (self.valor_inicial + (self.lance_minimo * self.n_lance))
        )
        return self.valor_arremate


class Pos_imissao(BaseModel):
    """Class to represent a Pos_imissao"""

    valor_reforma: float = 3000
    valor_desocupacao: float = 0
    # total: float

    def calculo_posimissao(self):
        """Calcular total = valor_reforma + valor_desocupacao"""
        return self.valor_reforma + self.valor_desocupacao


class Custo_arrematacao(BaseModel):
    """Class to represent a Custo_arrematacao"""

    valor_leiloero: float = Field(default=5.0, alias="Leiloero", ge=0)
    valor_ITBI: float = Field(default=5.0, alias="ITBI", ge=0)
    valor_registro: float = Field(default=0.01, alias="Registro", ge=0)
    valor_abogado: float = Field(default=4.0, alias="Abogado", ge=0)
    pc_comissao_leiloero: float
    pc_itbi: float
    pc_registro: float
    pc_abogado: float

    @model_validator(mode="before")
    @classmethod
    def validate_percentages(cls, values):
        values["pc_comissao_leiloero"] = values["Leiloero"] / 100
        values["pc_itbi"] = values["ITBI"] / 100
        values["pc_registro"] = values["Registro"] / 100
        values["pc_abogado"] = values["Abogado"] / 100
        return values

    def valor_comissao_leiloero(self, valor_arremate: float):
        """Calcular comissao leiloero = valor_arremate * pc_comissao_leiloero"""
        return self.pc_comissao_leiloero * valor_arremate

    def valor_itbi(self, valor_arremate: float):
        """Calcular ITBI = valor_arremate * pc_itbi"""
        return self.pc_itbi * valor_arremate

    def valor_total_registro(self, valor_arremate: float):
        """Calcular registro = valor_arremate * pc_registro"""
        return self.pc_registro * valor_arremate

    def calculo_custo_arramatacao(self, valor_arremate: float):
        """Calcular custo arrematacao = comissao leiloero + ITBI + Registro"""
        return (
            self.valor_comissao_leiloero(valor_arremate)
            + self.valor_itbi(valor_arremate)
            + self.valor_total_registro(valor_arremate)
        )


class Posposse(BaseModel):
    """Class to represent a Posposse"""

    praco_venda: int = 12

    def calculo_despesas(self, imovel: Imovel, parcela: float = 0):
        """Calcular despesas = custos mensais * praco_venda"""
        return imovel.custos_mensais(parcela) * self.praco_venda


class Impostos(BaseModel):
    """Class to represent a Impostos"""

    pc_imposto_ganho_capital: float = 0.15

    # @field_validator("pc_imposto_ganho_capital")
    # def val_to_per(cls, value):
    #     return value / 100

    def calculo_imposto_total(self, lucro: float):
        """Actualizar total = lucro * pc_imposto_ganho_capital"""
        total = self.pc_imposto_ganho_capital * lucro
        return total


class Results(BaseModel):
    total_despensas: float = Field(..., alias="Total Despesas")
    receta_liq: float = Field(..., alias="Receita Liquida")
    lucro_bruto: float = Field(..., alias="Lucro Bruto")
    lucro_liquido: float = Field(..., alias="Lucro Liquido")
    roi: float = Field(..., alias="ROI")
    total_arremate: float = Field(..., alias="Total Arremate")
    ganho_capital: float = Field(..., alias="Ganho Capital")


class CashFlow(BaseModel, arbitrary_types_allowed=True, extra="allow"):
    imovel: Imovel
    leilao: Leilao
    arrematacao: Custo_arrematacao
    extras: Pos_imissao
    posposse: Posposse
    impostos: Impostos
    bruto: float = 0
    liquido: float = 0
    roi: float = 0
    mortgage: Mortgage_price
    parcela: float
    financiamento: bool = False
    entrada: float = 0

    @model_validator(mode="before")
    def validate_mortgage(cls, values):
        values["leilao"]["Valor Arremate"] = values["leilao"]["Valor Inicial"] + (
            values["leilao"]["Lance minimo"] * values["leilao"]["Lance"]
        )

        values["mortgage"] = Mortgage_price(
            taxa=9.4,
            years=30,
            total=values["leilao"]["Valor Arremate"],
            entry=values["leilao"]["Valor Arremate"] * 0.1,
        )

        values["parcela"] = (
            values["mortgage"].calculate_mortage()[1]
            if "financiamento" in values
            else 0
        )
        values["entrada"] = values["leilao"]["Valor Arremate"] * values["pc_entrada"]
        return values

    def calculo_receta_liquida(self):
        """Calcular valor de venda. = Valor Venta * (1 - Comision)"""
        saldo_devedor = (
            self.mortgage.get_saldo(self.posposse.praco_venda)
            if self.financiamento
            else 0
        )
        self.receta_liquida = self.imovel.calculo_receita_liq(saldo_devedor)
        return self.receta_liquida

    def calculo_custo_arrematacao(self):
        """Calcular custo arrematacao. Total = Comissao Leiloero + ITBI + Registro"""
        self.custo_arrematacao = self.arrematacao.calculo_custo_arramatacao(
            self.leilao.valor_arremate
        )
        return self.custo_arrematacao

    def calculo_posimissao(self):
        """Calcular posimissao. Total = Valor Reforma + Valor Desocupacao"""
        self.posimissao = self.extras.calculo_posimissao()
        return self.posimissao

    def calculo_despensas_posposse(self):
        """Calcular posposse. Total = Custos mensais * prazo venda"""
        self.despensa_posposse = self.posposse.calculo_despesas(
            self.imovel, self.parcela
        )
        return self.despensa_posposse

    def calculo_imposto_ganho(self):
        """Calcular imposto ganho capital. Total = Ganho Capital * Imposto Ganho Capital"""
        self.imposto_ganho = self.impostos.calculo_imposto_total(
            self.calculo_ganho_capital()
        )
        return self.imposto_ganho

    def calculo_lucro_bruto(self, **kwargs):
        """Calcular lucro bruto. Total = Valor receita liquida - Valor Arremate - custos Arrermatacao - Valor Extra - Despesas Posposse"""
        self.lucro_b = (
            self.receta_liquida
            - self.calculo_custo_arrematacao()
            - self.leilao.valor_arremate
            - self.calculo_posimissao()
            - self.calculo_despensas_posposse()
            if not self.financiamento
            else self.receta_liquida
            - self.calculo_custo_arrematacao()
            - self.entrada
            - self.calculo_posimissao()
            - self.calculo_despensas_posposse()
        )
        return self.lucro_b

    def calculo_lucro_liquido(self, **kwargs):
        """Calcular lucro liquido. Total = Lucro Bruto - Despesas"""
        return self.lucro_b - self.calculo_imposto_ganho()

    def calculo_ganho_capital(self):
        """Calcular ganho capital = Valor Venta - Valor Arremate - Custo Arrematacao - Valor Reforma"""
        return (
            self.calculo_receta_liquida()
            - self.leilao.valor_arremate
            - self.custo_arrematacao
            - self.extras.valor_reforma
            if not self.financiamento
            else self.calculo_receta_liquida()
            - self.entrada
            - self.custo_arrematacao
            - self.extras.valor_reforma
        )

    def calculo_roi(self, **kwargs):
        """Calcular ROI = lucro liquido / valor de venda"""

        return self.calculo_lucro_liquido() / self.calculo_total_despesas()

    def calculo_total_despesas(
        self,
    ):
        """Calcular despesas. Total = Valor pago + Impostos + Posposse"""
        return (
            (
                self.leilao.valor_arremate
                + self.calculo_custo_arrematacao()
                + self.calculo_posimissao()
                + self.calculo_despensas_posposse()
            )
            if not self.financiamento
            else (
                self.entrada
                + self.calculo_custo_arrematacao()
                + self.calculo_posimissao()
                + self.calculo_despensas_posposse()
            )
        )

    def do_all(self):
        """Calcular todos os valores"""
        self.calculo_receta_liquida()
        self.calculo_custo_arrematacao()
        self.calculo_posimissao()
        self.calculo_despensas_posposse()
        self.calculo_imposto_ganho()
        self.calculo_lucro_bruto()
        self.calculo_lucro_liquido()
        self.calculo_ganho_capital()
        self.calculo_roi()
        self.calculo_total_despesas()
        return {
            "Entrada": self.entrada,
            "Total Despesas": self.calculo_total_despesas(),
            "Receita Liquida": self.calculo_receta_liquida(),
            "Lucro Bruto": self.calculo_lucro_bruto(),
            "Lucro Liquido": self.calculo_lucro_liquido(),
            "ROI": self.calculo_roi(),
            "Total Arremate": self.leilao.calculo_total_arremate(),
            "Ganho Capital": self.calculo_ganho_capital(),
        }
