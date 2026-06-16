export interface Periodo {
  inicio: string;
  fim: string;
}

export interface Tempo {
  anos: number;
  meses: number;
  dias: number;
}

export interface TempoContribuicaoItem {
  empregador: string;
  cnpj: string;
  funcao?: string | null;
  documento?: string | null;
  serie?: string | null;
  periodo_contribuicao: Periodo;
  periodo_aproveitado?: Periodo | null;
  tempo_contribuicao: Tempo;
  tempo_aproveitado?: Tempo | null;
}

export interface Salario {
  competencia: string;
  valor: number;
}

export interface DiscriminacaoSalario {
  empregador: string;
  cnpj: string;
  salarios: Salario[];
  competencias_faltantes: string[];
  falta_competencia: boolean;
}

export interface ResponseLeituraCTC {
  nome_requerente: string;
  orgao_instituidor: string;
  protocolo: string;
  tempo_contribuicao: TempoContribuicaoItem[];
  discriminacao_salarios_contribuicao: DiscriminacaoSalario[];
}
