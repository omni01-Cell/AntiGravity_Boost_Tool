import os
import sys
from parser import get_fisher_embeddings
from db_client import search_knowledge
from mcp_server import _plan_mcpo, _check_quality

def test_fisher_approximation():
    print("[Test] Verification de l'approximation de Fisher...")
    text = "L'architecture Mamba utilise des modeles d'espace d'etats (SSM) pour une recurrence lineaire."
    mu, var = get_fisher_embeddings(text)
    print(f" - Moyenne calculee (dim 0): {mu[0]}")
    print(f" - Variance calculee (dim 0): {var[0]}")
    assert len(mu) == 768
    assert len(var) == 768
    print("[OK] Fisher approximation validée.")

def test_looprag_cycle():
    print("[Test] Verification du cycle LoopRAG (Plan/Check)...")
    query = "Comment fonctionne la recurrence dans Mamba-3 ?"
    
    # Test Plan
    variants = _plan_mcpo(query)
    print(f" - Variantes PLAN : {variants}")
    assert len(variants) >= 1
    
    # Test Check
    mock_results = [{"content": "Mamba-3 utilise la regle trapezoidale pour la recurrence h_t = alpha*h_{t-1} + ..."}]
    audit = _check_quality(query, mock_results)
    print(f" - Audit CHECK : {audit}")
    assert "score" in audit
    
    print("[OK] Cycle LoopRAG validé.")

if __name__ == "__main__":
    try:
        test_fisher_approximation()
        test_looprag_cycle()
        print("\n[VERIFICATION REUSSIE] Le systeme SLM-V3 et LoopRAG sont operationnels.")
    except Exception as e:
        print(f"\n[VERIFICATION ECHOUEE] {e}")
        sys.exit(1)
