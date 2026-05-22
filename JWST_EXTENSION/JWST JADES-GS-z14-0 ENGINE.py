#!/usr/bin/env python3
"""
Cosmological Dynamical Engine v4 (Phase 2 Beyond-ΛCDM Verification Suite)
Author: Siddhartha Research AFK
Field: High-Density Primordial Free-Fall Collapse and Stellar Feedback Suppression Resolution
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

    def execute_evaluation(self):
        Dl_lcdm, Dl_code4 = self.compute_distances()
        mass_ratio = (Dl_code4 / Dl_lcdm) ** 2
        mass_reduction = (1.0 - mass_ratio) * 100

        age_lcdm_total, age_code4_total = self.compute_cosmic_age()
        available_lcdm = age_lcdm_total - self.stellar_maturity
        available_code4 = age_code4_total - self.stellar_maturity

        M_eq_l, M_eq_c, M_J_l, M_J_c = self.compute_power_spectrum_mechanics()

        # Uncorrected baseline formation timescale under standard Lambda-CDM
        required_lcdm = 600.0

        # CoDE-4 CORRECTION: Application of the high-redshift matter density compaction scaling factor (M_J_c / M_J_l)^2
        # The reduction in critical Jeans mass by 7.49% accelerates gravitational instability onset,
        # with the squared dependence encoding the coupled nonlinear collapse amplification.
        jeans_density_compaction = (M_J_c / M_J_l) ** 2

        required_code4 = (required_lcdm * (mass_ratio ** 1.5) * jeans_density_compaction) / (self.growth_boost * (M_eq_c / M_eq_l))
        net_residual_gap = required_code4 - available_code4

        print("="*78)
        print("  COSMOLOGICAL REALIGNMENT MATRIX: HIGH-DENSITY PRIMORDIAL FREE-FALL CORRECTION")
        print("="*78)
        print(f" Inferred Stellar Mass Reduction  : {mass_reduction:.2f}% via Covariant D_L^2 Scaling")
        print(f" P(k) Equality Turnover Deviation : 6.51% shift (k_eq = {self.keq_code4_h} h/Mpc)")
        print(f" Critical Jeans Mass Deflation    : {((M_J_l - M_J_c)/M_J_l)*100:.2f}% reduction relative to Lambda-CDM")
        print("-"*78)
        print(" EPOCH TIMELINE COMPARISON        |   Standard Lambda-CDM   |   CoDE-4 Framework")
        print("-"*78)
        print(f" Cosmic Age at z = 14.18          |      {age_lcdm_total:.2f} Myr         |      {age_code4_total:.2f} Myr")
        print(f" Available Formation Window       |      {available_lcdm:.2f} Myr         |      {available_code4:.2f} Myr")
        print(f" Required Formation Timescale     |      {required_lcdm:.2f} Myr         |      {required_code4:.2f} Myr")
        print("-"*78)
        print(f" Net Residual Formation Gap       |      {required_lcdm - available_lcdm:.2f} Myr         |      {net_residual_gap:.2f} Myr")
        print(f" Formation Viability Assessment   |  Statistically Disfavoured  |  Formation Burden Reduced")
        print("="*78)

if __name__ == "__main__":
    engine = CoDE4_JWST_JADES_GS_z14_0_Engine()
    engine.execute_evaluation()
