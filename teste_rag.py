import requests

# 1. Indexar alguns precedentes
precedentes = [
    "A multa contratual não pode exceder 10% do valor do contrato segundo o entendimento pacificado desta corte.",
    "No caso de cancelamento de voo sem aviso prévio, configura-se dano moral in re ipsa, sendo devida indenização ao passageiro.",
    "A eleição de foro estrangeiro em contrato de adesão no Brasil é considerada cláusula nula de pleno direito."
]

for i, p in enumerate(precedentes):
    res = requests.post("http://127.0.0.1:8000/jurisprudencia/indexar", json={
        "texto": p,
        "metadados": {"origem": "TJSP", "id_simulado": i}
    })
    print("Indexando:", res.json())

# 2. Buscar
print("\nBuscando...")
res = requests.post("http://127.0.0.1:8000/jurisprudencia/buscar", json={
    "query": "Qual o entendimento do tribunal sobre multa contratual abusiva?"
})
print(res.json())
