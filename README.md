# PINN Project - Physics over Capacity: Permanent Magnet Synchronous Motor (PMSM) Digital Twins under Scarce Supervision

> **Can Physics-Informed Neural Networks build accurate PMSM digital twins under scarce supervision?**

A PMSM digital twin must predict torque and internal temperatures from the signals an inverter already has for free: currents, voltages, and speed. Those targets are expensive to measure outside a test bench. This project asks whether embedding the motor's governing equations into the loss lets a network keep working as the expensive labels become scarce, while purely data-driven models degrade. Scarce supervision, not missing sensors: the input signals stay available everywhere, it is the labels that shrink.

The contribution, in one sentence:

> A controlled empirical study of whether coupled electromagnetic-thermal physics improves PMSM digital-twin accuracy, uncertainty, parameter stability, and interpretability as temperature labels become scarce. The comparison runs over a seven-rung ladder spanning pure physics to pure data: LPTN → XGBoost → MLP → LSTM → Transformer → TNN → PINN.

**Status: planning complete, execution not started. See [PLAN.md](PLAN.md) for the master plan.**

## The physics-informed twin

```
                             PMSM
                               │
                ┌──────────────┴──────────────┐
                ↓                             ↓
        Electromagnetic                    Thermal
           dynamics                        dynamics
                ↓                             ↓
        u_d, u_q, i_d, i_q         pm (rotor magnet temp)
        motor speed                stator winding / tooth / yoke
                                   coolant, ambient
                │                             │
                └──────────────┬──────────────┘
                               ↓
                             PINN
                               ↓
                ┌──────────────┼──────────────┐
                ↓              ↓              ↓
             Torque       Temperatures    Parameters
                                          R_s, L_d, L_q, ψ_f
```

The training loss is one supervised term plus four physics residuals, weighted per term:

$$
\mathcal{L} = \lambda_d L_{\mathrm{data}} + \lambda_{vd} L_{vd} + \lambda_{vq} L_{vq} + \lambda_T L_{\mathrm{torque}} + \lambda_{th} L_{\mathrm{thermal}}
$$

$L_{vd}$ and $L_{vq}$ are the dq voltage-equation residuals, $L_{\mathrm{torque}}$ the torque-equation residual, and $L_{\mathrm{thermal}}$ the lumped thermal-network ODE residual. The parameter outputs are the digital-twin part: $R_s, L_d, L_q, \psi_f$ drift with temperature and saturation in a real motor, and the network identifies them from data.

## The five studies

One repository, five self-contained report folders. Each has its own plan, scripts, notebooks, hypotheses, and invariant suite. Later studies carry the earlier data foundation over unchanged.

| Report | Study | One line |
|---|---|---|
| [sl-report](sl-report/) | Supervised Learning | the data foundation and the seven-rung ladder at full supervision |
| [ol-report](ol-report/) | Optimization & Uncertainty | loss weighting, physics-term ablation, collocation, conformal intervals, and the headline sparsity ladder |
| [ul-report](ul-report/) | Unsupervised Learning | operating-regime clustering (pointwise and temporal) and dimensionality reduction |
| [fe-report](fe-report/) | Feature Engineering | engineered, selected, and transformed feature sets, physics through the inputs |
| [xai-report](xai-report/) | Explainable AI | attributions, physics-native explanations, and whether explanations survive sparsity |

Execution order: sl → ol → ul → fe → xai.

## Data

Kaggle "Electric Motor Temperature" (`wkirgsn/electric-motor-temperature`, Paderborn University LEA test bench, version 3). 1,330,816 rows × 13 columns, 69 measurement sessions, 184.8 h at 2 Hz, physical units. The raw CSV lives in `sl-report/data/raw/` (not committed) and every study reads the processed splits from `sl-report/data/processed/` (committed once built).

## Discipline

Fixed seeds everywhere (sampling 746601, split 746602, models 7466/7467/7468). Session-grouped splits, preprocessing fit on training sessions only. The held-out test set is contacted exactly once per part by a dedicated test script. Hypotheses are pre-registered before any model runs and verified by a PASS/FAIL invariant script per study. Three-seed stability backs every claim.

## Repository layout

```
pinn-project-eee/
├── PLAN.md              # master plan
├── research-paper/      # 17 reference papers, review status per entry + index
├── sl-report/           # study 1 (owns data/)
├── ol-report/           # study 2
├── ul-report/           # study 3
├── fe-report/           # study 4
└── xai-report/          # study 5
```

Each report folder documents its own setup and run sequence in its README.
