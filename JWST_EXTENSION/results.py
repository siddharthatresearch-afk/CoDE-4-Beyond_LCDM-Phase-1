#!/usr/bin/env python3

"""
CoDE-4 JWST Extension Results Module
Author: Siddhartha Research AFK
Purpose:
    Execute the JWST extension engine and present
    scientific interpretation outputs in a structured format.
"""

import numpy as np
from scipy.integrate import quad

class CoDE4_JWST_JADES_GS_z14_0_Engine:
    def __init__(self):
        self.c = 299792.458
        self.sec_per_year = 31557600.0
        self.gyr_to_myr = 1000.0
        self.mpc_conversion = 3.085677581e19 / self.sec_per_year / 1e9
        self.G_const = 6.67430e-8
        self.mpc_to_cm = 3.08567758e24
        self.msun_to_g = 1.98847e33

        # Standard Lambda-CDM Baseline Parameters
        self.H0_lcdm = 67.4
        self.Om0 = 0.315
        self.Or0 = 9.4e-5
        self.Ode0 = 1.0 - self.Om0 - self.Or0
        self.keq_lcdm_h = 0.01675

        # CoDE-4 Perturbed Expansion Manifold Parameters
        self.H0_code4 = 72.86
        self.epsilon = 0.05
        self.keq_code4_h = 0.01566
        self.growth_boost = 1.0103

        # Observational Target: JADES-GS-z14-0
        self.z_target = 14.18
        self.stellar_maturity = 90.0

    def modifier_C(self, z):
        return 1.0 + self.epsilon * (z / (1.0 + z)**2) * (1.0 - 0.15 / (1.0 + z))

    def E_lcdm(self, z):
        return np.sqrt(self.Om0 * (1.0 + z)**3 + self.Or0 * (1.0 + z)**4 + self.Ode0)

    def E_code4(self, z):
        return np.sqrt(self.Om0 * (1.0 + z)**3 + self.Or0 * (1.0 + z)**4 + self.Ode0 * self.modifier_C(z))

    def compute_distances(self):
        integrand_lcdm = lambda z: self.c / (self.H0_lcdm * self.E_lcdm(z))
        integrand_code4 = lambda z: self.c / (self.H0_code4 * self.E_code4(z))
        Dc_lcdm, _ = quad(integrand_lcdm, 0, self.z_target)
        Dc_code4, _ = quad(integrand_code4, 0, self.z_target)
        return Dc_lcdm * (1.0 + self.z_target), Dc_code4 * (1.0 + self.z_target)

    def compute_cosmic_age(self):
        integrand_lcdm = lambda z: 1.0 / ((1.0 + z) * self.H0_lcdm * self.E_lcdm(z)) * self.mpc_conversion
        integrand_code4 = lambda z: 1.0 / ((1.0 + z) * self.H0_code4 * self.E_code4(z)) * self.mpc_conversion
        t_lcdm, _ = quad(integrand_lcdm, self.z_target, 2000)
        t_code4, _ = quad(integrand_code4, self.z_target, 2000)
        return t_lcdm * self.gyr_to_myr, t_code4 * self.gyr_to_myr

    def compute_power_spectrum_mechanics(self):
        h_lcdm = self.H0_lcdm / 100.0
        h_code4 = self.H0_code4 / 100.0
        keq_l_abs = self.keq_lcdm_h * h_lcdm
        keq_c_abs = self.keq_code4_h * h_code4

        rho_c0_l = (3.0 * (self.H0_lcdm * 1e5 / self.mpc_to_cm)**2) / (8.0 * np.pi * self.G_const)
        rho_c0_c = (3.0 * (self.H0_code4 * 1e5 / self.mpc_to_cm)**2) / (8.0 * np.pi * self.G_const)

        rho_m0_l = self.Om0 * rho_c0_l
        rho_m0_c = self.Om0 * rho_c0_c

        M_eq_l = (4.0 / 3.0) * np.pi * rho_m0_l * (np.pi / (keq_l_abs / self.mpc_to_cm))**3 / self.msun_to_g
        M_eq_c = (4.0 / 3.0) * np.pi * rho_m0_c * (np.pi / (keq_c_abs / self.mpc_to_cm))**3 / self.msun_to_g

        rho_m_z_l = rho_m0_l * (1.0 + self.z_target)**3
        rho_m_z_c = rho_m0_c * (1.0 + self.z_target)**3

        M_J_l = (np.pi / 6.0) * (np.pi / self.G_const)**1.5 * (rho_m_z_l)**-0.5 / self.msun_to_g
        M_J_c = (np.pi / 6.0) * (np.pi / self.G_const)**1.5 * (rho_m_z_c)**-0.5 / self.msun_to_g

        return M_eq_l, M_eq_c, M_J_l, M_J_c


def main():
    engine = CoDE4_JWST_JADES_GS_z14_0_Engine()

    # ------------------------------------------------------------
    # Execute Core Engine
    # ------------------------------------------------------------
    Dl_lcdm, Dl_code4 = engine.compute_distances()
    age_lcdm_total, age_code4_total = engine.compute_cosmic_age()
    M_eq_l, M_eq_c, M_J_l, M_J_c = engine.compute_power_spectrum_mechanics()

    # ------------------------------------------------------------
    # Geometric Stellar Mass Reduction
    # ------------------------------------------------------------
    mass_ratio = (Dl_code4 / Dl_lcdm) ** 2
    mass_reduction = (1.0 - mass_ratio) * 100

    # ------------------------------------------------------------
    # Matter Spectrum Turnover Sector
    # ------------------------------------------------------------
    turnover_shift = (
        abs(engine.keq_lcdm_h - engine.keq_code4_h)
        / engine.keq_lcdm_h
    ) * 100

    # ------------------------------------------------------------
    # Jeans Compaction Sector
    # ------------------------------------------------------------
    jeans_deflation = (
        (M_J_l - M_J_c) / M_J_l
    ) * 100

    jeans_density_compaction = (
        M_J_c / M_J_l
    ) ** 2

    # ------------------------------------------------------------
    # Cosmic Age Sector
    # ------------------------------------------------------------
    available_lcdm = (
        age_lcdm_total - engine.stellar_maturity
    )
    available_code4 = (
        age_code4_total - engine.stellar_maturity
    )

    # ------------------------------------------------------------
    # Formation Window Reduction
    # ------------------------------------------------------------
    required_lcdm = 600.0

    required_code4 = (
        required_lcdm
        * (mass_ratio ** 1.5)
        * jeans_density_compaction
    ) / (
        engine.growth_boost
        * (M_eq_c / M_eq_l)
    )

    net_gap_lcdm = (
        required_lcdm - available_lcdm
    )
    net_gap_code4 = (
        required_code4 - available_code4
    )

    # ------------------------------------------------------------
    # Scientific Results Output
    # ------------------------------------------------------------
    print("=" * 78)
    print("      CoDE-4 JWST EXTENSION : RESULTS MATRIX")
    print("=" * 78)

    print("\n[ GEOMETRIC LUMINOSITY-DISTANCE SECTOR ]")
    print("-" * 78)
    print(
        f"Inferred Stellar Mass Reduction : "
        f"{mass_reduction:.2f}%"
    )

    print("\n[ MATTER POWER SPECTRUM SECTOR ]")
    print("-" * 78)
    print(
        f"Turnover Deviation Shift        : "
        f"{turnover_shift:.2f}%"
    )
    print(
        f"Modified Equality Scale         : "
        f"{engine.keq_code4_h:.5f} h/Mpc"
    )

    print("\n[ JEANS COMPACTION SECTOR ]")
    print("-" * 78)
    print(
        f"Native Jeans Threshold Deflation : "
        f"{jeans_deflation:.2f}%"
    )
    print(
        f"Nonlinear Compaction Scaling     : "
        f"{jeans_density_compaction:.4f}"
    )

    print("\n[ GROWTH REFINEMENT SECTOR ]")
    print("-" * 78)
    print(
        f"Sigma-8 Growth Amplification : "
        f"{engine.growth_boost:.4f}"
    )

    print("\n[ COSMIC TIMELINE COMPARISON ]")
    print("-" * 78)
    print(
        f"LCDM Cosmic Age @ z=14.18      : "
        f"{age_lcdm_total:.2f} Myr"
    )
    print(
        f"CoDE-4 Cosmic Age @ z=14.18    : "
        f"{age_code4_total:.2f} Myr"
    )
    print(
        f"LCDM Available Formation Window : "
        f"{available_lcdm:.2f} Myr"
    )
    print(
        f"CoDE-4 Available Formation Window : "
        f"{available_code4:.2f} Myr"
    )

    print("\n[ REQUIRED FORMATION WINDOW ]")
    print("-" * 78)
    print(
        f"Standard LCDM Requirement : "
        f"{required_lcdm:.2f} Myr"
    )
    print(
        f"CoDE-4 Adjusted Requirement : "
        f"{required_code4:.2f} Myr"
    )

    print("\n[ RESIDUAL FORMATION GAP ]")
    print("-" * 78)
    print(
        f"LCDM Residual Formation Gap : "
        f"{net_gap_lcdm:.2f} Myr"
    )
    print(
        f"CoDE-4 Residual Formation Gap : "
        f"{net_gap_code4:.2f} Myr"
    )

    print("\n[ INTERPRETATION ]")
    print("-" * 78)
    print(
        "CoDE-4 demonstrates substantial reduction "
        "in early JWST formation pressure through "
        "coordinated expansion-growth evolution."
    )
    print(
        "The framework combines geometric mass reduction, "
        "equality modification, nonlinear Jeans compaction, "
        "and mild growth-sector amplification within "
        "a bounded phenomenological cosmology."
    )
    print("=" * 78)

if __name__ == "__main__":
    main()
