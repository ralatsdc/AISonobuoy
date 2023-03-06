ICA Source Separation for Hydrophone Audio Data
===============================================================================

-------------------------------------------------------------------------------

The ICA Source Separation project investigates the use of independent
component analysis (ICA) to extract source signals from audio clips with
multiple vessels present.

-------------------------------------------------------------------------------

Table of Contents
-----------------

1. [Overview][#1]

   1.1. [Theory][#1.1]

   1.2. [Summary of ICA Approaches and Results][#1.2]

   1.3. [Key Technical Outcomes][#1.3]

   1.4. [Future Directions][#1.4]

2. [Getting Started][#2]

   2.1. [Project Organization][#2.1]

   2.2. [Setting Up the Project][#2.2]

3. [Additional Information][#3]

-------------------------------------------------------------------------------

## 1. Overview

For details, see the [summary report](reports/ica-based-source-extraction.pdf).

### 1.1. Theory

Classically, ICA requires on multiple sensors. However, single-sensor ICA is
possible when the mixing coefficients for the source signals vary over time.
For moving sources generating acoustic waves, this condition is met because
the amplitude of the pressure varies with distance of the source from the
hydrophone.

### 1.2. Summary of ICA Approaches and Results

* __Time-domain ICA__

  Good source separation is achieved when source signals are phase-synchronized
  across recording times. When source signals are phase-unaligned across
  recording times, source separation is less effective.

* __Frequency-domain ICA with sine and cosine basis__

  This approach is not suitable for phase-unaligned recording times because the
  relative phase shifts in the source signals lead to coefficient mixing, which
  is inconsistent with the ICA signal model. Computational experiments confirm
  that source separation is not particularly effective for this approach.

* __Frequency-domain ICA with complex exponential basis__

  This is the most promising approach for source separation when source
  signals are phase-unaligned between recording times because (1) the
  frequency-domain signal model is consistent with the ICA signal model and
  (2) the relative phase shifts manifest as multiplicative changes to the
  mixing coefficients. Unfortunately, it was not possible to perform
  computational experiments to evaluate this approach because the `scikit-learn`
  FastICA implementation is limited to real-valued data.

### 1.3. Key Technical Outcomes

* Development of an ICA approach that is suitable for single-sensor systems
  when sources are in motion.

* Theoretical analysis of ICA-based approaches to source separation for source
signals that are phase-synchronized and phase-unaligned across multiple recording
times.

* Use of power spectra to characterize quasi-periodic source signals and assess
ICA source signal quality.

* Validation of theoretical expectations for ICA-based approaches via computational
experiments.

* Identification of potential key obstacle to a robust ICA approach for separating
quasi-periodic source signals.

### 1.4. Future Directions

* To assess the robustness of ICA for time-domain ICA, it would be beneficial to
        perform time-domain ICA on a wider range of synthetic datasets constructed over a
        wider range of vessel types, combinations, and number.

* Since time-domain ICA for phase-synchronized source signals showed good
        performance on synthetic datasets, it would be useful to perform experiments
        on non-synthetic datasets containing multiple vessels to determine whether it
        is reasonable to assume that real-world source signals are phase-synchronized.
        If so, time-domain ICA may be sufficient for feature engineering purposes.

* To assess the viability of frequency-domain ICA (using a complex exponential
        basis), it would be interesting to implement ICA for complex signals.
        Complex-valued ICA algorithms have been described in the
        literature~\cite{novey:2006,novey:2007,novey:2008,novey:2008b}, but they do not
        appear to have been ported to Python.

-------------------------------------------------------------------------------

## 2. Getting Started

#### 2.1. Project Organization

```
├── README.md          <- this file
├── requirements.in    <- input file to `pip-compile` (for generating
│                         `requirements.txt`
├── requirements.txt   <- project Python package dependencies (with version
│                         locks)
├── bin/               <- scripts and programs
├── data/              <- project data
├── extras/            <- additional files and references that may be useful
│                         for the project
├── notebooks/         <- Jupyter notebooks for project
└── reports/           <- project reports
```

#### 2.2. Setting Up the Project

* ___Prerequisites___

  * Install [Git][git].

  * Install [Python][python] 3.8 (or greater). __Recommendation__: use `pyenv`
    to configure the project to use a specific version of Python.

   * _Optional_. Install [direnv][direnv].

* Set up a dedicated virtual environment for the project. Any of the common
  virtual environment options (e.g., `venv`, `direnv`, `conda`) should work.
  Below are instructions for setting up a `direnv` environment.

  __Note__: to avoid conflicts between virtual environments, only one method
  should be used to manage the virtual environment.

  * __`direnv` Environment__. __Note__: `direnv` manages the environment for
    both Python and the shell.

    * ___Prerequisite___. Install `direnv`.

    * Copy `extras/dot-envrc` to the project root directory, and rename it to
      `.envrc`.

      ```shell
      $ cd $PROJECT_ROOT_DIR
      $ cp extras/dot-envrc .envrc
      ```

    * Grant permission to direnv to execute the .envrc file.

      ```shell
      $ direnv allow
      ```

* Upgrade `pip` to the latest released version.

  ```shell
  $ pip install --upgrade pip
  ```

* Install the Python packages required for the project.

  ```shell
  $ pip install -r requirement.txt
  ```

-------------------------------------------------------------------------------

### 3. Additional Information

* The `bin/generate-synthetic-dataset.py` script constructs synthetic audio
  clips by combining pure source clips using (1) the physics of acoustic wave
  propogation (linear approximation) and (2) simulated source motion
  (straight line motion).

* The summary report for the project is located at
  `reports/ica-based-source-extraction.pdf`. All source files required to
  generate the report is contained in the `reports` directory.

-------------------------------------------------------------------------------

[----------------------------- INTERNAL LINKS -----------------------------]: #

[#1]: #1-overview
[#1.1]: #11-theory
[#1.2]: #12-summary-of-ica-approaches-and-results
[#1.3]: #13-key-technical-outcomes
[#1.4]: #14-future-directions

[#2]: #2-getting-started
[#2.1]: #21-project-organization
[#2.2]: #22-setting-up-the-project

[#3]: #3-additional-information

[---------------------------- REPOSITORY LINKS ----------------------------]: #


[----------------------------- EXTERNAL LINKS -----------------------------]: #

[direnv]: https://direnv.net/
