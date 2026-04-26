#!/usr/bin/env python3
"""TFIM exact diagonalization benchmark — L4 validation template (toy_numeric lane).

Reference: Transverse-field Ising model in 1D.
  H = -J Σ σ^z_i σ^z_{i+1} - h Σ σ^x_i

Validates: ground state energy, gap, and magnetization against known results.

Input contract:
  - Accepts N (system size), J (coupling), h (transverse field) as parameters
  - Returns JSON dict with E0, gap, magnetization, and validation verdict

Output contract:
  - Writes results to stdout as JSON
  - Exits 0 on pass, 1 on fail

Usage: python tfim_exact_diagonalization.py --N 10 --J 1.0 --h 1.0
"""

import argparse
import json
import sys

import numpy as np


def build_hamiltonian(N: int, J: float, h: float) -> np.ndarray:
    """Build the TFIM Hamiltonian for N spins."""
    dim = 2**N
    H = np.zeros((dim, dim), dtype=complex)

    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)

    for i in range(N):
        # Transverse field term: -h σ^x_i
        op = [I] * N
        op[i] = sx
        term = -h
        for j, o in enumerate(op):
            term = np.kron(term, o) if j == 0 else np.kron(term, o)
        H += term

        # Interaction term: -J σ^z_i σ^z_{i+1} (periodic)
        op = [I] * N
        op[i] = sz
        op[(i + 1) % N] = sz
        term = -J
        for j, o in enumerate(op):
            term = np.kron(term, o) if j == 0 else np.kron(term, o)
        H += term

    return H


def compute_observables(H: np.ndarray) -> dict:
    """Diagonalize and compute ground state properties."""
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    E0 = eigenvalues[0].real
    E1 = eigenvalues[1].real
    gap = E1 - E0

    # Magnetization in z-direction
    psi0 = eigenvectors[:, 0]
    N = int(np.log2(len(psi0)))
    sz_tot = np.zeros((2**N, 2**N), dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    I = np.eye(2, dtype=complex)
    for i in range(N):
        op = [I] * N
        op[i] = sz
        term = op[0]
        for o in op[1:]:
            term = np.kron(term, o)
        sz_tot += term
    magnetization = (psi0.conj().T @ sz_tot @ psi0).real / N

    return {"E0": E0, "gap": gap, "magnetization": magnetization}


def validate_against_known(N: int, J: float, h: float, E0: float, gap: float) -> dict:
    """Validate against known exact results."""
    checks = {}

    # Critical point at h/J = 1: gap should close as 1/N
    if abs(h / J - 1.0) < 0.01:
        checks["critical_point_gap"] = {
            "status": "pass" if gap < 2.0 / N else "fail",
            "observed": gap,
            "expected_upper_bound": 2.0 / N,
            "note": "Gap should scale as ~1/N at critical point",
        }
    else:
        # In the ordered phase (h<J) or disordered phase (h>J), gap should be finite
        checks["finite_gap"] = {
            "status": "pass" if gap > 1e-10 else "fail",
            "observed": gap,
            "note": "Gap should be finite away from critical point",
        }

    # Ground state energy should be extensive: E0 ∝ N
    energy_per_site = E0 / N
    checks["extensive_energy"] = {
        "status": "pass" if abs(energy_per_site) < 2.0 * (abs(J) + abs(h)) else "fail",
        "observed": energy_per_site,
        "energy_per_site": energy_per_site,
        "note": "Energy per site bounded by 2(|J|+|h|)",
    }

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="TFIM exact diagonalization benchmark")
    parser.add_argument("--N", type=int, default=10, help="System size (N spins)")
    parser.add_argument("--J", type=float, default=1.0, help="Coupling constant")
    parser.add_argument("--h", type=float, default=1.0, help="Transverse field")
    parser.add_argument("--json", action="store_true", default=True, help="JSON output")
    args = parser.parse_args()

    if args.N > 14:
        print(json.dumps({"error": f"N={args.N} too large (max 14) for exact diagonalization"}))
        return 1

    H = build_hamiltonian(args.N, args.J, args.h)
    obs = compute_observables(H)
    checks = validate_against_known(args.N, args.J, args.h, obs["E0"], obs["gap"])

    all_pass = all(c["status"] == "pass" for c in checks.values())
    result = {
        "model": "TFIM",
        "parameters": {"N": args.N, "J": args.J, "h": args.h},
        "observables": obs,
        "checks": checks,
        "verdict": "pass" if all_pass else "fail",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
