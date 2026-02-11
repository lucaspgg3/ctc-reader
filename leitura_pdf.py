import io
import re
import pdfplumber
from copy import deepcopy
from datetime import datetime
from schemas import ResponseLeituraCTC
from dependencies import verificar_token
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

leituraCTC = APIRouter(prefix="/ctc-reader/api", tags=["CTC Reader"], dependencies=[Depends(verificar_token)])

# @leituraCTC.post("/leCTC")
@leituraCTC.post("/leCTC", response_model=ResponseLeituraCTC)
async def fazer_leitura(file: UploadFile = File(...)):

    def extract_text_from_bytes(file_bytes: bytes) -> str:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Arquivo deve ser um PDF válido")
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages_text)
        return text

    def extract_header_fields(text: str) -> dict:
        fields = {}

        # Nome do Requerente + Protocolo
        match = re.search(r"Nome do Requerente\s+Protocolo:\s*([^\n]+)\n+([A-Z\s]+)\s+NIT:", text)
        if match:
            fields["protocolo"] = match.group(1).strip()
            fields["nome_requerente"] = match.group(2).strip()

        # Órgão Instituidor
        match = re.search(r"Órgão Instituidor Matrícula\s*\n+([A-Z\s]+)\s+\d+", text)
        if match:
            fields["orgao_instituidor"] = match.group(1).strip()
        return fields

    def extract_tempo_contribuicao(text: str) -> list:
        bloco_match = re.search(r"A - TEMPO DE CONTRIBUIÇÃO(.*?)(?:DISCRIMINAÇÃO DOS SALÁRIOS DE CONTRIBUIÇÃO)", text, re.DOTALL)

        if not bloco_match:
            return []

        bloco = bloco_match.group(1)

        empregadores = re.split(r"\nEmpregador:\s*", bloco)
        registros = []

        for empregador in empregadores[1:]:
            registro = {}
            
            # Empregador
            match = re.match(r"([A-Z0-9\s\-\.\(\)]+)", empregador)
            if match:
                registro["empregador"] = match.group(1).strip().replace("\nN", "")

            # CNPJ
            match = re.search(r"Número:\s*([\d\.\-\/]+)", empregador)
            if match:
                registro["cnpj"] = match.group(1)

            # Documento e Série
            match = re.search(r"Documento:\s*(\d+)\s*-\s*CTPS Série:\s*(\d+)", empregador)
            if match:
                registro["documento"] = match.group(1)
                registro["serie"] = match.group(2)

            # Função
            match = re.search(r"Função:\s*([A-Z\s]+)", empregador)
            if match:
                funcao = match.group(1).strip().replace("\nP", "").strip()
                if funcao == "P":
                    registro["funcao"] = None
                else:
                    registro["funcao"] = funcao

            # Período de Contribuição
            match = re.search(r"Período Contribuição:\s*(\d{2}/\d{2}/\d{4})\s+a\s+(\d{2}/\d{2}/\d{4})", empregador)
            if match:
                registro["periodo_contribuicao"] = {
                    "inicio": match.group(1),
                    "fim": match.group(2)
                }

            # Período Aproveitado
            match = re.search(r"\*?Período Aproveitado:\s*(\d{2}/\d{2}/\d{4})\s+a\s+(\d{2}/\d{2}/\d{4})", empregador)
            if match:
                registro["periodo_aproveitado"] = {
                    "inicio": match.group(1),
                    "fim": match.group(2)
                }

            # Tempo de Contribuição
            match = re.search(r"Tempo de Contribuição:\s*(\d+)\s+ano\(s\),\s*(\d+)\s+mes\(es\),\s*(\d+)\s+dia\(s\)", empregador)
            if match:
                registro["tempo_contribuicao"] = {
                    "anos": int(match.group(1)),
                    "meses": int(match.group(2)),
                    "dias": int(match.group(3))
                }

            # Tempo Aproveitado
            match = re.search(r"Tempo Aproveitado:\s*(\d+)\s+ano\(s\),\s*(\d+)\s+mes\(es\),\s*(\d+)\s+dia\(s\)", empregador)
            if match:
                registro["tempo_aproveitado"] = {
                    "anos": int(match.group(1)),
                    "meses": int(match.group(2)),
                    "dias": int(match.group(3))
                }

            registros.append(registro)

        return registros

    def extract_discriminacao_salarios(text: str) -> list:
        bloco_match = re.search(r"DISCRIMINAÇÃO DOS SALÁRIOS DE CONTRIBUIÇÃO(.*)", text, re.DOTALL)

        if not bloco_match:
            return []

        bloco = bloco_match.group(1)
        empregadores = re.split(r"\nEmpregador:\s*", bloco)

        resultado = []

        for empregador in empregadores[1:]:
            nome = empregador.strip().split("\n", 1)[0].strip()
            cnpj_match = re.search(r"Número:\s*([\d\.\-\/]+)", empregador)
            cnpj = cnpj_match.group(1) if cnpj_match else None
            competencias = re.findall(r"(\d{2}/\d{4})\D+([\d\.]+,\d{2})", empregador)
            salarios = [
                {
                    "competencia": comp,
                    "valor": float(val.replace(".", "").replace(",", "."))
                }
                for comp, val in competencias
            ]

            resultado.append({
                "empregador": nome,
                "cnpj": cnpj,
                "salarios": salarios
            })

        return resultado

    def consolidar_salarios_por_empregador(dados: dict) -> dict:
        resultado = deepcopy(dados)

        agrupados = {}

        for item in dados.get("discriminacao_salarios_contribuicao", []):
            empregador = item["empregador"]

            if empregador not in agrupados:
                agrupados[empregador] = {
                    "empregador": item["empregador"],
                    "cnpj": item["cnpj"],
                    "salarios": []
                }

            agrupados[empregador]["salarios"].extend(item.get("salarios", []))

        # Ordena salários por competência (MM/AAAA)
        for emp in agrupados.values():
            emp["salarios"].sort(key=lambda x: (int(x["competencia"].split("/")[1]), int(x["competencia"].split("/")[0])))

        resultado["discriminacao_salarios_contribuicao"] = list(agrupados.values())
        return resultado
    
    def adicionar_verificacao_competencias(dados: dict) -> dict:
        resultado = deepcopy(dados)

        for empregador in resultado.get("discriminacao_salarios_contribuicao", []):
            salarios = empregador.get("salarios", [])

            if not salarios:
                empregador["competencias_faltantes"] = []
                empregador["falta_competencia"] = False
                continue

            datas_existentes = [
                datetime.strptime(s["competencia"], "%m/%Y")
                for s in salarios
            ]

            data_inicio = min(datas_existentes)
            data_fim = max(datas_existentes)
            competencias_esperadas = []
            data_atual = data_inicio

            while data_atual <= data_fim:
                competencias_esperadas.append(data_atual.strftime("%m/%Y"))
                if data_atual.month == 12:
                    data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
                else:
                    data_atual = data_atual.replace(month=data_atual.month + 1)
            competencias_existentes = {s["competencia"] for s in salarios}
            faltantes = [
                comp for comp in competencias_esperadas
                if comp not in competencias_existentes
            ]
            empregador["competencias_faltantes"] = faltantes
            empregador["falta_competencia"] = len(faltantes) > 0

        return resultado

    file_bytes = await file.read()

    text = extract_text_from_bytes(file_bytes)

    resultado = {
        **extract_header_fields(text),
        "tempo_contribuicao": extract_tempo_contribuicao(text),
        "discriminacao_salarios_contribuicao": extract_discriminacao_salarios(text)
    }

    resultado_formatado = consolidar_salarios_por_empregador(resultado)
    resultado_final = adicionar_verificacao_competencias(resultado_formatado)

    return resultado_final