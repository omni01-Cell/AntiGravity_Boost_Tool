import time
import statistics
import logging
from typing import List
from core.services.ingestion_service import IngestionService

# Désactiver les logs verbeux pour le benchmark
logging.getLogger("core.services").setLevel(logging.ERROR)

def benchmark_ingestion_pipeline():
    """Mesure les performances du pipeline sur un cycle réel."""
    service = IngestionService()
    
    sample_texts = [
        "The SOLID principles are a set of five design principles in object-oriented computer programming.",
        "Riemannian geometry is the branch of differential geometry that studies Riemannian manifolds.",
        "Stochastic Langevin dynamics define the evolution of a system under noise and cost.",
    ] * 5 # 15 chunks total
    
    delays = []
    print(f"Démarrage du benchmark sur {len(sample_texts)} chunks...")
    
    for i, text in enumerate(sample_texts):
        start_time = time.perf_counter()
        
        # On simule l'ingestion sans l'écriture finale en BDD si on veut tester le calcul pur
        # Ou on laisse tout si on veut le "real world"
        success = service._ingest_chunk(text, f"bench_{i}.txt")
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        delays.append(duration)
        
        status = "OK" if success else "BLOCKED"
        print(f"Chunk {i+1}/{len(sample_texts)}: {duration:.3f}s [{status}]")

    # Résultats
    avg = statistics.mean(delays)
    p95 = statistics.quantiles(delays, n=20)[18] if len(delays) >= 20 else max(delays)
    
    print("\n" + "="*30)
    print("RÉSULTATS DU BENCHMARK")
    print("="*30)
    print(f"Temps moyen par chunk : {avg:.3f}s")
    print(f"Temps P95             : {p95:.3f}s")
    print(f"Throughput estimé    : {1/avg:.2f} chunks/sec")
    print("="*30)

if __name__ == "__main__":
    benchmark_ingestion_pipeline()
