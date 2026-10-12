"""Independent analytic controls and rejection tests for the delivered kit."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from scipy.linalg import expm

from agentkit.checkpoint import load_latest, save_checkpoint
from agentkit.demo import run_demo
from agentkit.evidence import (canonical, closure_status, evaluate_receipt,
                               freeze, inside, sha256_file, snapshot, verify_snapshot,
                               write_new_json)
from agentkit.learning import (MODELS, objective, paired_accuracy, prepare_data,
                               scores_and_directions)
from agentkit.mesh import compile_passive, decompose_unitary, reconstruct
from agentkit.metrology import fit_cutback, system_energy
from agentkit.numerics import (coherent_decomposition, exact_discrete_transport,
                               generalized_modes, mass_power, optical_error_budget,
                               phase_metrics, spatial_forecast, spatial_holdout,
                               splitting_control, transfer_sensitivity,
                               logarithmic_norm, residual_error_bound, detector_error_bound)
from agentkit.paraxial import grid, run_resumable, split_step
from agentkit.supervisor import supervise


class NumericalTests(unittest.TestCase):
    def test_dissipative_mass_generator_growth(self):
        m = np.diag([2.0, 3.0])
        a = -0.2*m + 1j*np.diag([1.0, 2.0])
        self.assertAlmostEqual(logarithmic_norm(a, m), -0.2)

    def test_residual_bound_recovers_exact_constant_forcing(self):
        result = residual_error_bound([0, 0.5, 1.0], [0.1, 0.1], 0.2, -0.3)
        expected = 0.2*np.exp(-0.3) + 0.1*(1-np.exp(-0.3))/0.3
        self.assertAlmostEqual(result, expected)

    def test_psd_detector_error_bound(self):
        u, e = np.array([1, 2j]), np.array([0.01j, 0.02])
        d, m = np.diag([0.4, 0.8]), np.diag([2, 3])
        measured = abs(np.vdot(u+e, d@(u+e))-np.vdot(u, d@u))
        bound = detector_error_bound(u, m, d, np.sqrt(mass_power(e, m)))
        self.assertLessEqual(measured, bound)

    def test_coherent_cross_term_cannot_be_discarded(self):
        u = np.array([1, 1j])
        r = np.array([[1], [1]], complex)
        dual = np.array([[1], [0]], complex)
        record = coherent_decomposition(u, r, np.ones(2), dual)
        self.assertAlmostEqual(record["total_power"], 2)
        self.assertAlmostEqual(record["cross_power"], -2)
        self.assertLess(record["balance_error"], 1e-12)

    def test_mass_orthogonal_projection(self):
        record = coherent_decomposition([1, 2j], [[1], [0]], [2, 3])
        self.assertAlmostEqual(record["total_power"], 14)
        self.assertAlmostEqual(record["cross_power"], 0)

    def test_nonpositive_mass_rejected(self):
        with self.assertRaises(ValueError):
            mass_power([1, 2], [1, -1])

    def test_nonnormal_eigenpair_condition(self):
        record = generalized_modes([[1, 4], [0, 2]], [1, 1])
        self.assertLess(record["relative_residuals"].max(), 1e-12)
        self.assertGreater(record["eigenvalue_condition_indicators"].max(), 4)

    def test_strang_second_order_on_fixed_smooth_matrices(self):
        a, b = 1j*np.array([[0, 1], [1, 0]]), 1j*np.diag([0.4, -0.4])
        errors = [splitting_control(a, b, [1, 0], 1, n)["relative_field_error"]
                  for n in (8, 16, 32)]
        self.assertTrue(3.8 < errors[0]/errors[1] < 4.2)
        self.assertTrue(3.8 < errors[1]/errors[2] < 4.2)

    def test_commuting_split_is_exact(self):
        result = splitting_control(1j*np.diag([1, 2]), 1j*np.diag([3, 4]), [1, 1j], 0.4, 3)
        self.assertLess(result["relative_field_error"], 1e-12)

    def test_frechet_derivative_matches_finite_difference(self):
        h, dh = np.array([[0, 0.5], [0.5, 0]]), np.diag([0.3, -0.2])
        result = transfer_sensitivity(h, dh, 0.8)
        epsilon = 1e-6
        reference = (expm(0.8j*(h+epsilon*dh))-expm(0.8j*(h-epsilon*dh)))/(2*epsilon)
        self.assertLess(np.linalg.norm(result["derivative"]-reference), 1e-8)

    def test_absolute_phase_error_is_retained(self):
        result = phase_metrics([1, 1], 1j*np.ones(2), np.ones(2))
        self.assertAlmostEqual(result["max_phase_error_rad"], np.pi/2)
        self.assertGreater(result["relative_field_error"], 1)

    def test_dark_field_does_not_divide_by_zero(self):
        result = phase_metrics([0, 0], [0, 0], [1, 1])
        self.assertIsNone(result["relative_field_error"])
        self.assertIsNone(result["max_phase_error_rad"])

    def test_s16_exact_law_and_heldout(self):
        h = np.array([1, 0.8, 0.64, 0.512])
        p = 0.333 + 0.002*h**2
        result = spatial_holdout(p[:3], [1e-10]*3, p[3], 1e-10, 1e-10, 1e-10)
        self.assertTrue(result["passed"])

    def test_s16_oscillation_and_temporal_noise_rejected(self):
        self.assertFalse(spatial_forecast([1, 2, 1.5], [0, 0, 0])["eligible"])
        self.assertFalse(spatial_forecast([1, 1.1, 1.15], [0.1]*3)["eligible"])

    def test_wavelength_interval_must_exclude_zero(self):
        with self.assertRaises(ValueError):
            optical_error_budget(1, 1, 1, 0, 0, 1)

    def test_transport_translation_and_mass_rejection(self):
        x = np.array([[0, 0], [1, 0]])
        result = exact_discrete_transport(x, [0.5, 0.5], x+[0, 0.2], [0.5, 0.5])
        self.assertAlmostEqual(result["wasserstein2"], 0.2, places=8)
        with self.assertRaises(ValueError):
            exact_discrete_transport(x, [1, 1], x, [0.5, 0.5])


class CompilerTests(unittest.TestCase):
    def test_complex_unitary_reconstruction(self):
        rng = np.random.default_rng(42)
        q, _ = np.linalg.qr(rng.standard_normal((6, 6))+1j*rng.standard_normal((6, 6)))
        compiled = decompose_unitary(q)
        self.assertLess(np.linalg.norm(reconstruct(compiled)-q), 1e-11)

    def test_passive_nondiagonal_target(self):
        q = expm(1j*np.array([[0.1, 0.7], [0.7, -0.3]]))
        target = q @ np.diag([0.9, 0.2]) @ q.T
        compiled = compile_passive(target)
        self.assertLess(np.linalg.norm(reconstruct(compiled)-target), 1e-12)
        self.assertFalse(compiled["geometry_validated"])

    def test_amplification_is_rejected(self):
        with self.assertRaises(ValueError):
            compile_passive(1.01*np.eye(2))


class PersistenceTests(unittest.TestCase):
    def test_atomic_checkpoint_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            marker = save_checkpoint(root, np.ones((2, 2), complex), 0, 10, "a"*64, None)
            next_marker = save_checkpoint(root, 2*np.ones((2, 2), complex), 5, 10,
                                          "a"*64, sha256_file(marker))
            state, step, _ = load_latest(root, "a"*64, 10)
            self.assertEqual(step, 5)
            self.assertTrue(np.all(state == 2))
            with self.assertRaises(FileExistsError):
                save_checkpoint(root, state, 5, 10, "a"*64, sha256_file(marker))
            record = json.loads(next_marker.read_text())
            (root/record["array_file"]).write_bytes(b"corrupt")
            with self.assertRaises(ValueError):
                load_latest(root, "a"*64, 10)

    def test_resume_matches_uninterrupted_trajectory(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (x, y), _ = grid(16, 64e-6)
            field = np.exp(-(x*x+y*y)/(8e-6)**2).astype(complex)
            profile = np.where(x < 0, -0.003, 0.0)
            source = root/"input.npz"
            np.savez(source, field=field, delta_n=profile)
            config = {"width_m": 64e-6, "wavelength_m": 1550e-9,
                      "n_reference": 1.444, "length_m": 20e-6, "steps": 7}
            result = run_resumable(source, config, root/"checkpoints", 2, 40)
            restored, step, _ = load_latest(root/"checkpoints", result["experiment_hash"], 7)
            expected = field
            for _ in range(7):
                expected = split_step(expected, profile, 64e-6, 1550e-9, 1.444, 20e-6/7)
            self.assertEqual(step, 7)
            np.testing.assert_array_equal(restored, expected)
            second = run_resumable(source, config, root/"checkpoints", 2, 40)
            self.assertEqual(second["steps_at_entry"], 7)

    def test_snapshot_rejects_mutation_and_traversal(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root/"input.txt").write_text("original")
            record = snapshot(root, ["input.txt"])
            (root/"input.txt").write_text("changed")
            with self.assertRaises(ValueError):
                verify_snapshot(root, record)
            with self.assertRaises(ValueError):
                inside(root, "../input.txt")

    def test_receipt_cannot_turn_partial_execution_into_pass(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.name=Kit Test",
                            "-c", "user.email=kit@example.invalid", "commit", "--allow-empty",
                            "-qm", "manufactured test"], check=True)
            protocol = {"experiment_id": "test", "task_id": "T01", "model": "fixture",
                        "units": {"length": "m"}, "scope": "manufactured_control",
                        "criteria": [{"id": "error", "operator": "le", "threshold": 0.1}],
                        "resource_limits": {"seconds": 1}, "heldout_policy": "fixture"}
            write_new_json(root/"protocol.json", protocol)
            (root/"source.py").write_text("x = 1\n")
            (root/"raw.csv").write_text("value\n0.05\n")
            frozen = freeze(root, "protocol.json", ["source.py"], root/"frozen.json")
            result = {"experiment_id": "test", "protocol_sha256": hashlib.sha256(canonical(protocol)).hexdigest(),
                      "scope": "manufactured_control", "status": "partial",
                      "artifacts": ["raw.csv"], "metrics": {"error": 0.05}}
            with self.assertRaises(ValueError):
                evaluate_receipt(root, frozen, result)
            result["status"] = "completed"
            result["metrics"] = {}
            self.assertFalse(evaluate_receipt(root, frozen, result)["passed"])
            result["metrics"] = {"error": 0.05}
            self.assertTrue(evaluate_receipt(root, frozen, result)["passed"])

    def test_numerical_audit_does_not_close_physical_task(self):
        task = {"scope": "physical_device", "requires": []}
        self.assertEqual(closure_status(task, {"scope": "numerical", "passed": True}, {}),
                         "BLOCKED_SCOPE")

    def test_supervisor_timeout(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            report = supervise([sys.executable, "-c", "import time; time.sleep(5)"],
                               root, root/"log.txt", root/"report.json", 0.2, 0, 0)
            self.assertEqual(report["status"], "timeout")
            self.assertNotEqual(report["exit_code"], 0)


class LearningAndMeasurementTests(unittest.TestCase):
    def test_analytic_gradients_for_all_models(self):
        rng = np.random.default_rng(9)
        x = rng.normal(size=(7, 3))
        y = np.arange(7) % 3
        for model in MODELS:
            with self.subTest(model=model):
                size = 18 if "_" in model else 9
                p = rng.normal(scale=0.2, size=size)
                loss, gradient = objective(p, x, y, model, 2.3, 0.1)
                numerical = np.zeros(size)
                for i in range(size):
                    delta = np.zeros(size)
                    delta[i] = 1e-6
                    high = objective(p+delta, x, y, model, 2.3, 0.1)[0]
                    low = objective(p-delta, x, y, model, 2.3, 0.1)[0]
                    numerical[i] = (high-low)/2e-6
                self.assertTrue(np.isfinite(loss))
                np.testing.assert_allclose(gradient, numerical, atol=3e-7, rtol=3e-5)

    def test_cascaded_unitaries_preserve_linear_function_class(self):
        rng = np.random.default_rng(3)
        u, v = expm(1j*np.diag([0.2, 0.4])), expm(1j*np.array([[0, 1], [1, 0]]))
        x = rng.normal(size=(10, 2))
        np.testing.assert_allclose((x @ u.T) @ v.T, x @ (v @ u).T, atol=1e-14)

    def test_bootstrap_reports_observed_difference_exactly(self):
        result = paired_accuracy([0, 1, 0, 0], [0, 0, 1, 0], [0, 1, 1, 0], 200)
        self.assertEqual(result["observed_difference"], 0.0)

    def test_data_preprocessing_uses_training_only(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            rng = np.random.default_rng(13)
            x = rng.normal(size=(90, 4))
            y = np.repeat(np.arange(3), 30)
            np.savez(root/"raw.npz", X=x, y=y)
            first = prepare_data(root/"first", root/"raw.npz", 42)
            with np.load(root/"first"/"test.npz") as data:
                test_indices = data["raw_indices"]
            x[test_indices] += 100000
            np.savez(root/"changed.npz", X=x, y=y)
            second = prepare_data(root/"second", root/"changed.npz", 42)
            np.testing.assert_allclose(first["mean"], second["mean"], atol=0)
            np.testing.assert_allclose(first["pca_components"], second["pca_components"], atol=0)

    def test_manufactured_cutback_recovers_known_slope(self):
        with tempfile.TemporaryDirectory() as name:
            report = run_demo(Path(name)/"demo")["manufactured_cutback"]
            self.assertAlmostEqual(report["mean_loss_db_per_cm"], 0.1, places=10)
            self.assertLess(report["ci95"][0], 0.1)
            self.assertGreater(report["ci95"][1], 0.1)

    def test_whole_system_energy_includes_all_components(self):
        rows = [{"time_s": i, "completed_inferences": i*10, "source_w": 1,
                 "modulation_w": 1, "detection_w": 1, "control_w": 1, "cooling_w": 1}
                for i in range(3)]
        result = system_energy(rows)
        self.assertAlmostEqual(result["total_energy_j"], 10)
        self.assertAlmostEqual(result["joules_per_inference"], 0.5)
        rows[1]["time_s"] = 0
        with self.assertRaises(ValueError):
            system_energy(rows)

    def test_split_step_does_not_renormalize_loss(self):
        (x, y), dx = grid(16, 64e-6)
        field = np.ones_like(x, dtype=complex)
        output = split_step(field, np.zeros_like(x), 64e-6, 1550e-9,
                            1.444, 1e-6, np.full_like(x, 1e5))
        ratio = np.sum(abs(output)**2) / np.sum(abs(field)**2)
        self.assertAlmostEqual(ratio, np.exp(-0.2), places=12)


if __name__ == "__main__":
    unittest.main()
