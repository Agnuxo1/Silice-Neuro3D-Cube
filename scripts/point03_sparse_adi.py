"""Unvalidated SuperLU draft for a prospective ADI equivalence audit.

No fields are propagated on import. The factory keeps the supplied Stepper's
constructor, Laplacian, and stepping equations intact. This draft is not yet
scientific evidence and must not replace a frozen study's solver.
"""
from __future__ import annotations

import copy
import hashlib
import time


class RejectedPermutationError(ValueError):
    """Carry observed factor metadata and raw permutations across setup failure."""
    def __init__(self, diagnostic, permutation_arrays):
        super().__init__("Unexpected SuperLU permutation; equivalence requires review.")
        self.diagnostic = diagnostic
        self.permutation_arrays = permutation_arrays


def make_sparse_stepper(original_stepper):
    """Return a subclass overriding only the cached factors and their solves.

    Pass the untouched ``adi2d.Stepper`` class from an explicitly verified
    source module. SciPy is imported only when this factory is called.
    """
    import numpy as np
    import scipy
    from scipy.sparse import diags
    from scipy.sparse.linalg import splu

    def permutation_metadata(values):
        values = np.asarray(values)
        expected = np.arange(values.size, dtype=values.dtype)
        return {"length": int(values.size), "dtype": str(values.dtype),
                "identity": bool(np.array_equal(values, expected)),
                "nonidentity_entries": int(np.count_nonzero(values != expected)),
                "sha256": hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()}

    class SuperLUStepper(original_stepper):
        """The original ADI equations with full, disjoint-block sparse LU."""

        def _fact(self, diagonal):
            started = time.perf_counter()
            # The inherited constructor calls _fact twice, before any _solve.
            if not hasattr(self, "_sparse_stats"):
                self._sparse_stats = {
                    "backend": "scipy.sparse.linalg.splu",
                    "scipy_version": scipy.__version__, "numpy_version": np.__version__,
                    "original_class": original_stepper.__module__ + "." + original_stepper.__qualname__,
                    "options": {"permc_spec": "NATURAL", "diag_pivot_thresh": 0.0,
                                "Equil": False},
                    "factors": [], "validation_status": "requires_paired_audit_result"}
            diagonal = np.asarray(diagonal)
            if (diagonal.ndim != 2 or diagonal.shape[0] != diagonal.shape[1]
                    or diagonal.shape[0] < 2 or diagonal.dtype != np.dtype("complex128")
                    or not np.all(np.isfinite(diagonal))):
                raise ValueError("Expected a finite, square complex128 diagonal grid.")
            n = diagonal.shape[0]
            size = n * n
            lower = np.full(size - 1, self.sub, dtype=np.complex128)
            upper = np.full(size - 1, self.sup, dtype=np.complex128)
            # In C order each line is a separate tridiagonal block. These cuts
            # prevent the end of one line from coupling to the next line.
            cuts = np.arange(n - 1, size - 1, n)
            lower[cuts] = 0
            upper[cuts] = 0
            matrix = diags((lower, diagonal.ravel(order="C"), upper),
                           offsets=(-1, 0, 1), shape=(size, size),
                           format="csc", dtype=np.complex128)
            matrix.eliminate_zeros()
            matrix.sort_indices()
            expected_nnz = 3 * n * n - 2 * n
            if matrix.nnz != expected_nnz:
                raise ValueError("Unexpected nonzero count in the disjoint-block matrix.")
            assembled = time.perf_counter()
            lu = splu(matrix, permc_spec="NATURAL", diag_pivot_thresh=0.0,
                      options={"Equil": False})
            factored = time.perf_counter()
            row_permutation = permutation_metadata(lu.perm_r)
            column_permutation = permutation_metadata(lu.perm_c)
            lower_factor, upper_factor = lu.L, lu.U
            def csc_bytes(array):
                return int(array.data.nbytes + array.indices.nbytes + array.indptr.nbytes)
            metadata = {
                "factor_index": len(self._sparse_stats["factors"]),
                "line_count": n, "line_size": n, "matrix_order": size,
                "matrix_nnz": int(matrix.nnz), "expected_matrix_nnz": expected_nnz,
                "L_nnz": int(lower_factor.nnz), "U_nnz": int(upper_factor.nnz),
                "matrix_csc_bytes": csc_bytes(matrix),
                "factor_export_csc_bytes": csc_bytes(lower_factor) + csc_bytes(upper_factor),
                "storage_scope": "CSC arrays only; excludes native SuperLU workspace and Python overhead.",
                "perm_r": row_permutation, "perm_c": column_permutation,
                "assembly_s": assembled - started, "factorization_s": factored - assembled,
                "solve_calls": 0, "solve_elapsed_s": 0.0}
            metadata["setup_elapsed_s"] = time.perf_counter() - started
            self._sparse_stats["factors"].append(metadata)
            # Retain the actual observations even if the inherited constructor
            # cannot return an instance because a permutation is rejected.
            if not row_permutation["identity"] or not column_permutation["identity"]:
                raise RejectedPermutationError(copy.deepcopy(self._sparse_stats),
                                               {"perm_r": np.array(lu.perm_r, copy=True),
                                                "perm_c": np.array(lu.perm_c, copy=True)})
            return {"lu": lu, "matrix": matrix, "shape": diagonal.shape, "metadata": metadata}

        def _solve(self, factor, rhs):
            started = time.perf_counter()
            rhs = np.asarray(rhs)
            if rhs.shape != factor["shape"] or rhs.dtype != np.dtype("complex128"):
                raise ValueError("RHS shape or dtype differs from its cached factor.")
            # The inherited y sweep already passes rhs2.T.copy() and restores
            # the returned transpose. Both solves here are normal systems.
            result = factor["lu"].solve(rhs.ravel(order="C"), trans="N")
            result = result.reshape(factor["shape"], order="C")
            factor["metadata"]["solve_calls"] += 1
            factor["metadata"]["solve_elapsed_s"] += time.perf_counter() - started
            return result

        def sparse_metadata(self):
            """Return JSON-compatible costs and permutation identities, not LU arrays."""
            return copy.deepcopy(self._sparse_stats)

    return SuperLUStepper
