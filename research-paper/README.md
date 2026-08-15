# Research Papers for the Permanent Magnet Synchronous Motor (PMSM) Digital Twin Project

Seventeen papers, collected 2026-08-15. Files are the authors' arXiv copies of peer-reviewed work, with exceptions recorded per entry: the founding PINN paper is present as the publisher's version of record, and three competing-work preprints carry their review status in their rows. The venue is recorded per paper below. Files are named `<year>_<first-author>_<slug>.pdf` by the peer-reviewed publication year. When the project git repository is initialized, the PDFs stay out of version control and this index is committed.

## Domain: motor temperature estimation on this exact dataset

| File | Paper | Peer-reviewed venue | Used by |
|---|---|---|---|
| `2021_kirchgaessner_motor-temp-supervised-ml-benchmark.pdf` | Kirchgässner, Wallscheid, Böcker, "Data-Driven Permanent Magnet Temperature Estimation in Synchronous Motors with Supervised Machine Learning" (arXiv 2001.06246) | IEEE Transactions on Energy Conversion, 2021 | sl. The dataset authors' own benchmark. Source of the EWMA feature practice B1-B2 follow, and the reference our full-supervision numbers are read against |
| `2023_kirchgaessner_thermal-neural-networks.pdf` | Kirchgässner, Wallscheid, Böcker, "Thermal Neural Networks: Lumped-Parameter Thermal Modeling With State-Space Machine Learning" (arXiv 2103.16323) | Engineering Applications of Artificial Intelligence, 2023 | sl, xai. The TNN family our B5 rung implements, and the published state of the art on this dataset |
| `2021_zhang_ml-for-electric-drives-review.pdf` | Zhang, Wallscheid, Porrmann, "Machine Learning for the Control and Monitoring of Electric Machine Drives: Advances and Trends" (arXiv 2110.05403) | IEEE Open Journal of Industry Applications, 2021 | all. The domain survey placing digital twins, thermal monitoring, and ML drives work in one map |

## Physics-informed neural networks

| File | Paper | Peer-reviewed venue | Used by |
|---|---|---|---|
| `2019_raissi_pinn-jcp-published.pdf` | Raissi, Perdikaris, Karniadakis, "Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations" (doi 10.1016/j.jcp.2018.10.045) | Journal of Computational Physics 378, 686-707, 2019. The publisher's version of record, merging Parts I and II | sl, ol, xai. The citation of record for every PINN claim in the reports |
| `2019_raissi_pinn-part1.pdf` | Raissi, Perdikaris, Karniadakis, "Physics Informed Deep Learning (Part I): Data-driven Solutions" (arXiv 1711.10561) | merged into the JCP paper above | sl, ol. The founding forward-problem formulation our composite loss follows |
| `2019_raissi_pinn-part2-discovery.pdf` | Raissi, Perdikaris, Karniadakis, "Physics Informed Deep Learning (Part II): Data-driven Discovery" (arXiv 1711.10566) | merged into the JCP paper above | sl, ol, xai. The discovery formulation: unknown physical parameters as trainable variables, which is exactly our `R_s, L_d, L_q, ψ_f` identification and the H3 recovery test |
| `2022_cuomo_pinn-survey.pdf` | Cuomo et al., "Scientific Machine Learning through Physics-Informed Neural Networks: Where we are and What's next" (arXiv 2201.05624) | Journal of Scientific Computing, 2022 | sl, ol. The survey grounding design choices and known failure modes |
| `2021_wang_pinn-gradient-pathologies.pdf` | Wang, Teng, Perdikaris, "Understanding and mitigating gradient pathologies in physics-informed neural networks" (arXiv 2001.04536) | SIAM Journal on Scientific Computing, 2021 | ol. Why residual terms fight each other and the learning-rate-annealed weighting that motivates the λ pilot |

## Loss weighting and multi-task balance (the ol λ pilot's three candidates)

| File | Paper | Peer-reviewed venue | Used by |
|---|---|---|---|
| `2018_kendall_uncertainty-task-weighting.pdf` | Kendall, Gal, Cipolla, "Multi-Task Learning Using Uncertainty to Weigh Losses" (arXiv 1705.07115) | CVPR 2018 | ol. The learned log-variance weighting, pilot candidate (ii) |
| `2018_chen_gradnorm.pdf` | Chen et al., "GradNorm: Gradient Normalization for Adaptive Loss Balancing" (arXiv 1711.02257) | ICML 2018 (PMLR 80) | ol. The gradient-norm balancing behind pilot candidate (iii) |

## Uncertainty quantification (ol Part 5)

| File | Paper | Peer-reviewed venue | Used by |
|---|---|---|---|
| `2017_lakshminarayanan_deep-ensembles.pdf` | Lakshminarayanan, Pritzel, Blundell, "Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles" (arXiv 1612.01474) | NeurIPS 2017 | ol. The seed-ensemble member of Part 5 |
| `2023_angelopoulos_conformal-intro.pdf` | Angelopoulos, Bates, "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification" (arXiv 2107.07511) | Foundations and Trends in Machine Learning, 2023 | ol. The split-conformal recipe and its exchangeability caveats, stated in our risks |

## Explainability (xai)

| File | Paper | Peer-reviewed venue | Used by |
|---|---|---|---|
| `2017_lundberg_shap.pdf` | Lundberg, Lee, "A Unified Approach to Interpreting Model Predictions" (arXiv 1705.07874) | NeurIPS 2017 | xai. TreeSHAP for the XGBoost rung |
| `2019_jain_attention-not-explanation.pdf` | Jain, Wallace, "Attention is not Explanation" (arXiv 1902.10186) | NAACL 2019 | xai. The reason Transformer attention maps stay descriptive and never enter comparison tables |

## Directly competing work (the papers the reports must position against)

Added 2026-08-15 after the novelty review flagged the gap. These are the closest 2024-2026 physics-informed PMSM temperature papers.

| File | Paper | Status | Why it competes |
|---|---|---|---|
| `2025_liao_complex-neural-dynamics-pmsm.pdf` | Liao, Chen, Zhao, "Parallelizable Complex Neural Dynamics Models for PMSM Temperature Estimation with Hardware Acceleration" (arXiv 2511.16093) | arXiv preprint, Nov 2025, peer-review status unverified at collection time | physics-informed thermal dynamics on the same Paderborn dataset, the TNN lineage our B5 rung competes in |
| `2025_winkler_mhe-thermal-derating.pdf` | Winkler, Shah, Baumgärtner et al., "Incorporating a Deep Neural Network into Moving Horizon Estimation for Embedded Thermal Torque Derating of an Electric Machine" (arXiv 2504.12736) | arXiv preprint, 2025, peer-review status unverified | the deployment side of the same problem: NN plus estimator for thermal derating |
| `2026_elhussieny_residual-pinn-bldc.pdf` | El-Hussieny, "Residual Physics-Informed Neural Networks for High-Fidelity BLDC Motor Modeling" (arXiv 2607.09136) | arXiv preprint, Jul 2026, peer-review status unverified | residual-PINN electric-motor modeling, adjacent machine type |
| not stored | Sheng, Liu, Chen, Zhu, Huang, Wang, "OLTEM: Lumped Thermal and Deep Neural Model for PMSM Temperature" | AI (MDPI) 6(8):173, 2025, peer-reviewed, open access. The publisher blocks scripted downloads, adding it is one browser click at doi 10.3390/ai6080173 | LPTN embedded in a recurrent state space with attention and a power-loss sub-network, a direct TNN-line competitor |
| not stored | "Hybrid Thermal Modeling With LPTN-Informed Neural Network for Multinode Temperature Estimation in PMSM" | IEEE Transactions on Power Electronics, 2024 (IEEE Xplore 10547453), no arXiv copy | the closest LPTN-informed LSTM competitor, cited from the published record |

The sl and ol related-work sections must position against all five, and the reports state which claims each one already covers.

## Known gaps, stated plainly

- Kirchgässner's "Estimating Electric Motor Temperatures with Deep Residual Machine Learning" (IEEE Transactions on Power Electronics, 2021) has no arXiv copy, so it is cited in the reports from the abstract and the published metrics rather than stored here.
- Wallscheid's thermal-monitoring state-of-the-art review (IEEE OJIA) is open access at IEEE but not on arXiv. It can be added manually from the publisher page if wanted.
- Venue attributions come from the papers themselves and the publisher records. Anything cited in a report gets its venue re-verified at writing time.
