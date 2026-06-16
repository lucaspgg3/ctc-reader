from pydantic import BaseModel
from typing import List, Optional

class Periodo(BaseModel):
    inicio: str
    fim: str

class Tempo(BaseModel):
    anos: int
    meses: int
    dias: int

class TempoContribuicaoItem(BaseModel):
    empregador: str
    cnpj: str
    funcao: Optional[str] = None
    documento: Optional[str] = None
    serie: Optional[str] = None
    periodo_contribuicao: Periodo
    periodo_aproveitado: Optional[Periodo] = None
    tempo_contribuicao: Tempo
    tempo_aproveitado: Optional[Tempo] = None

class Salario(BaseModel):
    competencia: str
    valor: float

class DiscriminacaoSalario(BaseModel):
    empregador: str
    cnpj: str
    salarios: List[Salario]
    competencias_faltantes: List[str] = []
    falta_competencia: bool = False

class ResponseLeituraCTC(BaseModel):
    nome_requerente: str
    orgao_instituidor: str
    protocolo: str
    tempo_contribuicao: List[TempoContribuicaoItem]
    discriminacao_salarios_contribuicao: List[DiscriminacaoSalario]

    class Config:
        from_attributes = True