import os
import sys
import pandas as pd
from datasets import load_dataset

print("Gerando arquivos de backup offline para a apresentação...")

token = os.environ.get("HF_TOKEN")

print("1. Baixando STJ...")
stj = load_dataset("andrebadini/repojus", name="tribunal-stj", split="train[:50]", token=token)
stj.to_pandas().to_parquet("stj_reserva.parquet")

print("2. Baixando TJSP...")
tjsp = load_dataset("andrebadini/repojus", name="tribunal-tjsp", split="train[:50]", token=token)
tjsp.to_pandas().to_parquet("tjsp_reserva.parquet")

print("Backup offline criado com sucesso! Arquivos: stj_reserva.parquet e tjsp_reserva.parquet")
